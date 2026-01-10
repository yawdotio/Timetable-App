"""
File parser utility for extracting data from PDFs, Excel, and CSV files
Updates: Handles hierarchical headers (MultiIndex) and Time indexes.
"""
import pdfplumber
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dateutil import parser as date_parser
import re


class FileParser:
    """Parse various file formats to extract timetable data"""
    
    def __init__(self):
        self.supported_formats = {'.pdf', '.xlsx', '.xls', '.csv'}
    
    def parse_file(self, file_path: str, file_type: str, sheet_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Parse a file and return structured data
        """
        file_type = file_type.lower()
        
        if file_type == '.pdf':
            return self.parse_pdf(file_path)
        elif file_type in ['.xlsx', '.xls']:
            return self.parse_excel(file_path, sheet_name=sheet_name)
        elif file_type == '.csv':
            return self.parse_csv(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
    
    def _process_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Core Logic: Detects hierarchical headers and restructures the DataFrame.
        Handles logic where headers are split across rows (e.g., Row 1: Mon/Tue, Row 2: Course/Room).
        """
        # 1. Clean completely empty rows/cols to start
        df = df.dropna(how="all").dropna(axis=1, how="all")
        if df.empty:
            return df

        # 2. Search for Hierarchical Header (Time/Day + Attribute)
        search_limit = min(20, len(df))
        header_found = False
        header_idx = -1
        
        # Keywords to identify the 'Day' row and 'Attribute' row
        day_keywords = {
            'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
            'mon', 'tue', 'tues', 'wed', 'thu', 'thur', 'thurs', 'fri', 'sat', 'sun'
        }
        attr_keywords = {
            'course', 'subject', 'module', 'title', 'class', 'type',
            'venue', 'room', 'room no', 'rm', 'location', 'building', 'hall', 'lab', 'address',
            'teacher', 'instructor', 'lecturer', 'tutor', 'code'
        }
        
        # Heuristic search for the header pattern
        for i in range(search_limit - 1):
            row_curr = df.iloc[i].astype(str).str.lower()
            row_next = df.iloc[i+1].astype(str).str.lower()
            
            days_found = sum(1 for cell in row_curr if any(d in cell for d in day_keywords))
            attrs_found = sum(1 for cell in row_next if any(a in cell for a in attr_keywords))
            
            # If we find day names in one row and attributes in the next
            if days_found >= 1 and attrs_found >= 2:
                header_idx = i
                header_found = True
                break

        if header_found:
            # --- Normalize Hierarchy (UNPIVOT Logic) ---
            row_days_raw = df.iloc[header_idx].copy()
            row_attrs = df.iloc[header_idx + 1].copy()

            # Forward fill to cover merged cells (so Course/Venue under Monday get Monday)
            row_days_ffill = row_days_raw.replace({'nan': None, 'NaN': None, '': None}).ffill()

            # Identify common columns (e.g., Time, Period - columns that don't belong to a specific Day)
            common_cols_indices = []
            for i, val in enumerate(row_days_ffill):
                val_str = str(val).strip().lower()
                is_empty = val is None or val_str in ('', 'nan', 'nan', 'none')
                is_day = any(d in val_str for d in day_keywords)
                
                if is_empty or not is_day:
                    common_cols_indices.append(i)

            # Identify day columns
            day_cols_indices = []
            for i, _ in enumerate(row_days_ffill):
                if i not in common_cols_indices:
                    day_cols_indices.append(i)

            # Unique ordered list of days present
            unique_days = []
            for i in day_cols_indices:
                dval = str(row_days_ffill.iloc[i]).strip()
                if dval and dval not in unique_days:
                    unique_days.append(dval)

            # Body starts after the two header rows
            data_body = df.iloc[header_idx + 2:].copy()
            normalized_chunks: List[pd.DataFrame] = []

            def _name_for_common(idx: int) -> str:
                name = str(row_attrs.iloc[idx]).strip()
                if not name or name.lower() in ('nan', 'none', ''):
                    # Fallback to row_days if row_attrs is empty
                    return str(row_days_raw.iloc[idx]).strip() or 'Time'
                return name

            # Build chunk per day
            for day in unique_days:
                current_day_indices = [i for i in day_cols_indices if str(row_days_ffill.iloc[i]).strip() == day]
                if not current_day_indices:
                    continue

                day_attr_names = [str(row_attrs.iloc[i]).strip() for i in current_day_indices]
                
                # Logic to detect repeating attributes (e.g. 2 slots per day: Course, Venue, Course, Venue)
                # This splits one day into multiple rows if patterns repeat
                base_pattern = []
                if len(day_attr_names) > 1:
                    first_attr = day_attr_names[0]
                    if day_attr_names.count(first_attr) > 1:
                        try:
                            # Try to find the repetition cycle
                            second_idx = day_attr_names.index(first_attr, 1)
                            candidate_pattern = day_attr_names[:second_idx]
                            # Check consistency
                            if len(day_attr_names) % len(candidate_pattern) == 0:
                                base_pattern = candidate_pattern
                        except ValueError:
                            pass 
                
                if not base_pattern:
                    base_pattern = day_attr_names

                pattern_width = len(base_pattern)
                
                # Create sub-chunks if pattern repeats, otherwise just one chunk
                num_repeats = 1
                if len(current_day_indices) > pattern_width and len(current_day_indices) % pattern_width == 0:
                    num_repeats = len(current_day_indices) // pattern_width

                for r in range(num_repeats):
                    start_ptr = r * pattern_width
                    end_ptr = start_ptr + pattern_width
                    sub_indices = current_day_indices[start_ptr:end_ptr]

                    cols_to_select = common_cols_indices + sub_indices
                    chunk = data_body.iloc[:, cols_to_select].copy().reset_index(drop=True)

                    common_names = [_name_for_common(idx) for idx in common_cols_indices]
                    new_col_names = common_names + base_pattern
                    
                    chunk.columns = self._fit_column_names(new_col_names, chunk.shape[1])
                    
                    # Forward-fill common columns (like Time) 
                    if common_names:
                        c_slice = list(chunk.columns[:len(common_names)])
                        chunk[c_slice] = chunk[c_slice].replace(['', 'nan', 'None', None], pd.NA).ffill()

                    chunk = chunk.dropna(how='all', subset=[c for c in chunk.columns if c not in common_names])
                    
                    if not chunk.empty:
                        chunk['Day'] = day
                        normalized_chunks.append(chunk)

            if normalized_chunks:
                df = pd.concat(normalized_chunks, ignore_index=True)
                # Reorder to put Day and Time first
                common_names = self._clean_columns([_name_for_common(idx) for idx in common_cols_indices])
                leading_cols = ['Day'] + [n for n in common_names if n in df.columns]
                other_cols = [c for c in df.columns if c not in leading_cols]
                df = df[leading_cols + other_cols]
            else:
                # Fallback: hierarchy detected but normalization failed
                df = df.iloc[header_idx + 2:].copy()
                df.columns = self._clean_columns(df.columns)
        
        else:
            # --- Fallback: Standard Header (No Hierarchy) ---
            if not df.empty:
                # Assume first non-empty row is header
                header_row = list(df.iloc[0].values)
                df = df.iloc[1:].copy()
                df.columns = self._fit_column_names(self._clean_columns(header_row), df.shape[1])

        df = df.reset_index(drop=True)
        return df
    
    def parse_pdf(self, file_path: str) -> Dict[str, Any]:
        """
        Extract tables from PDF using pdfplumber and normalize like Excel/CSV
        """
        try:
            frames: List[pd.DataFrame] = []
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    tables = page.extract_tables()
                    for table in tables:
                        if not table:
                            continue
                        # Convert table (list of lists) into DataFrame; keep header rows for detection
                        df_tab = pd.DataFrame(table)
                        if df_tab.empty:
                            continue
                        # Normalize via the same hierarchical detection used for Excel/CSV
                        df_norm = self._process_dataframe(df_tab)
                        if df_norm.empty:
                            continue
                        frames.append(df_norm.fillna(""))

            if frames:
                combined = pd.concat(frames, ignore_index=True, sort=False).fillna("")
                data = combined.astype(str).to_dict("records")
                # Post-process: split/normalize time ranges and clean rows
                data = self._process_time_ranges(data, list(combined.columns))
                suggested = self._detect_columns(list(combined.columns))
                return {
                    "columns": list(combined.columns),
                    "data": data,
                    "available_sheets": [],
                    "sheet_used": None,
                    "suggested_mapping": suggested,
                }

            # If no tabular data, fallback to text extraction
            all_data = self._extract_text_from_pdf(file_path)
            columns = list(all_data[0].keys()) if all_data else []
            return {
                "columns": columns,
                "data": all_data,
                "available_sheets": [],
                "sheet_used": None,
                "suggested_mapping": self._detect_columns(columns) if columns else {}
            }

        except Exception as e:
            raise Exception(f"Error parsing PDF: {str(e)}")
    
    def _extract_text_from_pdf(self, file_path: str) -> List[Dict[str, Any]]:
        """Fallback: Extract text line by line when no tables found"""
        data = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    lines = text.split('\n')
                    for line in lines:
                        if line.strip():
                            parts = re.split(r'\s{2,}', line.strip())
                            data.append({
                                "raw_text": line.strip(),
                                "parts": parts
                            })
        return data
    
    def parse_excel(self, file_path: str, sheet_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Parse Excel file using pandas (supports multi-sheet workbooks)
        """
        try:
            excel_file = pd.ExcelFile(file_path)
            best_df: Optional[pd.DataFrame] = None
            best_sheet: Optional[str] = None
            best_score: Tuple[int, int] = (0, 0) # (rows, cols)

            target_sheets = [sheet_name] if sheet_name and sheet_name in excel_file.sheet_names else excel_file.sheet_names

            for sheet in target_sheets:
                # header=None is CRITICAL to allow _process_dataframe to find the header manually
                df = excel_file.parse(sheet_name=sheet, dtype=str, header=None)
                
                # Apply the logic
                df = self._process_dataframe(df)
                
                if df.empty:
                    continue

                df = df.fillna("")
                score = (len(df), len(df.columns))

                # Simple heuristic: prefer the sheet with most data
                if score > best_score:
                    best_score = score
                    best_df = df
                    best_sheet = sheet

            if best_df is None:
                # Fallback if no specific sheet logic worked, try reading first sheet normally
                raise Exception("No usable tabular data found in Excel file.")

            data = best_df.astype(str).to_dict("records")
            suggested = self._detect_columns(list(best_df.columns))
            
            # Post-process time ranges
            data = self._process_time_ranges(data, list(best_df.columns))

            return {
                "columns": list(best_df.columns),
                "data": data,
                "sheet_used": best_sheet,
                "available_sheets": excel_file.sheet_names,
                "suggested_mapping": suggested,
            }
        except Exception as e:
            raise Exception(f"Error parsing Excel: {str(e)}")
    
    def parse_csv(self, file_path: str) -> Dict[str, Any]:
        """
        Parse CSV file using pandas
        """
        try:
            encodings = ["utf-8", "latin-1", "iso-8859-1", "cp1252"]
            df = None

            for encoding in encodings:
                try:
                    # Load with header=None to manually detect layout
                    df = pd.read_csv(file_path, encoding=encoding, dtype=str, header=None)
                    break
                except UnicodeDecodeError:
                    continue

            if df is None:
                raise Exception("Could not decode CSV file with supported encodings.")

            # Apply the logic
            df = self._process_dataframe(df)
            df = df.fillna("")

            data = df.astype(str).to_dict("records")
            suggested = self._detect_columns(list(df.columns))
            
            # Post-process time ranges
            data = self._process_time_ranges(data, list(df.columns))

            return {
                "columns": list(df.columns),
                "data": data,
                "suggested_mapping": suggested,
                "available_sheets": [],
                "sheet_used": None,
            }
        except Exception as e:
            raise Exception(f"Error parsing CSV: {str(e)}")
    
    @staticmethod
    def fuzzy_date_parse(date_string: str) -> str:
        try:
            cleaned = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', date_string)
            parsed_date = date_parser.parse(cleaned, fuzzy=True)
            return parsed_date.strftime('%Y-%m-%d')
        except Exception:
            return date_string

    @staticmethod
    def extract_time(time_string: str) -> Dict[str, str]:
        pattern = r'(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?)\s*[-–]\s*(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?)'
        match = re.search(pattern, time_string)
        if match:
            return {'start_time': match.group(1).strip(), 'end_time': match.group(2).strip()}
        
        single_pattern = r'(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?)'
        match = re.search(single_pattern, time_string)
        if match:
            return {'start_time': match.group(1).strip(), 'end_time': None}
        
        return {'start_time': time_string, 'end_time': None}

    @staticmethod
    def _clean_columns(columns: List[Any]) -> List[str]:
        cleaned = []
        seen = {}
        for idx, col in enumerate(columns):
            name = str(col).strip() if col is not None else ""
            name = name or f"Column_{idx+1}"
            
            # Handle duplicates by appending suffix
            if name in seen:
                seen[name] += 1
                name = f"{name}_{seen[name]}"
            else:
                seen[name] = 0
            
            cleaned.append(name)
        return cleaned

    @staticmethod
    def _fit_column_names(names: List[Any], n_cols: int) -> List[str]:
        """Ensure the provided names list matches the number of DataFrame columns.
        - Truncates if too long
        - Pads with generic names if too short
        Always returns cleaned, unique names of length n_cols.
        """
        # Normalize incoming names to strings first
        norm = [str(n).strip() if n is not None else "" for n in names]
        if n_cols <= 0:
            return []
        if len(norm) >= n_cols:
            return FileParser._clean_columns(norm[:n_cols])
        # pad
        padded = norm + [f"Column_{i+1}" for i in range(len(norm), n_cols)]
        return FileParser._clean_columns(padded)
    
    def _process_time_ranges(self, data: List[Dict[str, Any]], columns: List[str]) -> List[Dict[str, Any]]:
        """Process time ranges (START-END) and clean empty string values"""
        time_col = next((c for c in columns if 'time' in c.lower() or 'period' in c.lower()), None)
        
        processed_data = []
        for row in data:
            # Skip completely empty rows
            non_empty = [v for v in row.values() if str(v).strip() and str(v).lower() not in ('nan', 'none', '')]
            if not non_empty:
                continue
            
            cleaned_row = {}
            for key, value in row.items():
                val_str = str(value).strip()
                if val_str.lower() in ['nan', 'none', '']:
                    cleaned_row[key] = ""
                else:
                    cleaned_row[key] = val_str
            
            if time_col and cleaned_row.get(time_col):
                time_val = cleaned_row[time_col]
                # Normalize spaces in ranges "9:00 - 10:00" -> "9:00-10:00"
                match = re.search(r'(\d{1,2}:\d{2})\s*[-–]\s*(\d{1,2}:\d{2})', time_val)
                if match:
                    cleaned_row[time_col] = f"{match.group(1)}-{match.group(2)}"
            
            processed_data.append(cleaned_row)
        return processed_data

    @staticmethod
    def _detect_columns(columns: List[str]) -> Dict[str, Optional[str]]:
        patterns = {
            "date": ["date", "day", "weekday", "day name"],
            "time": ["time", "times", "period", "session", "slot", "start"],
            "end_time": ["end", "finish", "until", "to"],
            "title": ["title", "event", "name", "subject", "course", "module", "class"],
            "location": ["location", "room", "venue", "place", "hall", "lab"],
            "description": ["description", "notes", "instructor", "teacher", "lecturer"]
        }
        mapping: Dict[str, Optional[str]] = {k: None for k in patterns.keys()}
        
        for col in columns:
            col_l = col.lower().strip()
            # Exact matches priorities
            if col_l in ("day", "weekday") and not mapping["date"]: mapping["date"] = col
            elif col_l == "time" and not mapping["time"]: mapping["time"] = col
            elif col_l in ["course", "subject"] and not mapping["title"]: mapping["title"] = col
            elif col_l == "venue" and not mapping["location"]: mapping["location"] = col
        
        # Fuzzy match
        for col in columns:
            if col in mapping.values():
                continue
            col_l = col.lower()
            for key, keywords in patterns.items():
                if not mapping[key] and any(kw in col_l for kw in keywords):
                    mapping[key] = col
                    break
        return mapping
