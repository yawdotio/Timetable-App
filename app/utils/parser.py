"""
File parser utility for extracting data from PDFs, Excel, and CSV files
Updates: Handles hierarchical headers (MultiIndex) and Time indexes.
"""
import pdfplumber
import pandas as pd
import numpy as np
from pathlib import Path
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
        Internal: Detects headers (hierarchical or standard) and restructures the DataFrame.
        Handles cases where headers are split across multiple rows (e.g., Days -> Attributes).
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
        
        for i in range(search_limit - 1):
            # Get rows as lowercase strings for checking
            row_curr = df.iloc[i].astype(str).str.lower()
            row_next = df.iloc[i+1].astype(str).str.lower()
            
            # Count matches
            days_found = sum(1 for cell in row_curr if any(d in cell for d in day_keywords))
            attrs_found = sum(1 for cell in row_next if any(a in cell for a in attr_keywords))
            
            # Heuristic: If we find day names in one row and attributes in the next
            if days_found >= 1 and attrs_found >= 2:
                header_idx = i
                header_found = True
                break

        if header_found:
            # --- Normalize Hierarchy (UNPIVOT) ---
            # Row A (header_idx): Days (e.g., Monday, NaN, Tuesday, ...)
            # Row B (header_idx+1): Attributes (e.g., Course, Venue, ...)

            # Keep raw to detect common columns, and an ffilled copy to group per-day
            row_days_raw = df.iloc[header_idx].copy()
            row_attrs = df.iloc[header_idx + 1].copy()

            # Forward fill to cover merged cells (so Course/Venue under Monday get Monday)
            row_days_ffill = row_days_raw.replace({'nan': None, 'NaN': None, '': None}).ffill()

            # Identify common columns (no day label OR has non-day label in RAW header row)
            # Common columns are things like "Time", "Period" that apply to all days
            common_cols_indices = []
            for i, val in enumerate(row_days_ffill):
                if val is None or str(val).strip() in ('', 'nan', 'NaN'):
                    common_cols_indices.append(i)
                else:
                    # Check if this is NOT a day name (e.g., "Time", "Period")
                    val_str = str(val).strip().lower()
                    if not any(d in val_str for d in day_keywords):
                        common_cols_indices.append(i)

            # Identify day columns (have a day label after ffill AND matches day keywords)
            day_cols_indices = []
            for i, val in enumerate(row_days_ffill):
                if val is not None and str(val).strip() not in ('', 'nan', 'NaN'):
                    val_str = str(val).strip().lower()
                    if any(d in val_str for d in day_keywords):
                        day_cols_indices.append(i)

            # Unique ordered list of days present across columns
            unique_days = []
            for i in day_cols_indices:
                dval = str(row_days_ffill.iloc[i]).strip()
                if dval and dval not in unique_days:
                    unique_days.append(dval)

            # Body starts after the two header rows
            data_body = df.iloc[header_idx + 2:].copy()

            normalized_chunks: List[pd.DataFrame] = []

            # Helper to derive column names for common columns (e.g., Time/Period)
            def _name_for_common(idx: int) -> str:
                name = str(row_attrs.iloc[idx]).strip()
                if not name or name.lower() in ('nan', 'none'):
                    # Fallback to whatever is in days row, else Time
                    fallback = str(row_days_raw.iloc[idx]) if idx < len(row_days_raw) else ''
                    fallback = (fallback or '').strip()
                    return fallback or 'Time'
                return name

            # Build chunk per day
            for day in unique_days:
                current_day_indices = [i for i in day_cols_indices if str(row_days_ffill.iloc[i]).strip() == day]
                if not current_day_indices:
                    continue

                day_attr_names = [str(row_attrs.iloc[i]).strip() for i in current_day_indices]
                
                # Detect repeating attribute pattern (e.g., [Course, Venue, Course, Venue])
                base_pattern = []
                if day_attr_names:
                    first_attr = day_attr_names[0]
                    if day_attr_names.count(first_attr) > 1:
                        try:
                            second_occurrence_idx = day_attr_names.index(first_attr, 1)
                            p = day_attr_names[:second_occurrence_idx]
                            # Verify the pattern is consistent
                            if len(day_attr_names) % len(p) == 0:
                                is_consistent = all(day_attr_names[i] == p[i % len(p)] for i in range(len(day_attr_names)))
                                if is_consistent:
                                    base_pattern = p
                        except ValueError:
                            pass  # No second occurrence
                
                if not base_pattern:
                    base_pattern = day_attr_names
                
                pattern_width = len(base_pattern) if base_pattern else 0
                day_chunks = []
                
                if pattern_width > 0 and len(current_day_indices) % pattern_width == 0:
                    num_repeats = len(current_day_indices) // pattern_width
                    
                    for i in range(num_repeats):
                        start_idx = i * pattern_width
                        end_idx = start_idx + pattern_width
                        sub_indices = current_day_indices[start_idx:end_idx]
                        
                        cols_to_select = common_cols_indices + sub_indices
                        chunk = data_body.iloc[:, cols_to_select].copy().reset_index(drop=True)
                        
                        common_names = [_name_for_common(idx) for idx in common_cols_indices]
                        new_col_names = common_names + base_pattern
                        # Fit and clean column names to the actual number of columns
                        fitted_names = self._fit_column_names(new_col_names, chunk.shape[1])
                        chunk.columns = fitted_names

                        # Forward-fill common columns (like Time) for multi-line entries
                        if common_names and chunk.shape[1] > 0:
                            # The first len(common_names) columns correspond to the common columns
                            num_common = min(len(common_names), chunk.shape[1])
                            common_slice = list(chunk.columns[:num_common])
                            chunk[common_slice] = chunk[common_slice].replace(['', 'nan', 'None', None], pd.NA).ffill()
                        
                        # Drop rows that are entirely empty after ffill
                        chunk = chunk.dropna(how='all', subset=[c for c in chunk.columns if c not in common_names])
                        
                        if not chunk.empty:
                            day_chunks.append(chunk)

                    if day_chunks:
                        # Stack the unpivoted chunks vertically
                        day_df = pd.concat(day_chunks, ignore_index=True)
                        day_df['Day'] = day
                        normalized_chunks.append(day_df)
                else: # Fallback for irregular structure
                    chunk = data_body.iloc[:, common_cols_indices + current_day_indices].copy()
                    common_names = [_name_for_common(idx) for idx in common_cols_indices]
                    new_col_names = common_names + day_attr_names
                    # Fit and clean column names to the actual number of columns
                    fitted_names = self._fit_column_names(new_col_names, chunk.shape[1])
                    chunk.columns = fitted_names
                    if common_names and chunk.shape[1] > 0:
                        num_common = min(len(common_names), chunk.shape[1])
                        common_slice = list(chunk.columns[:num_common])
                        chunk[common_slice] = chunk[common_slice].replace(['', 'nan', 'None', None], pd.NA).ffill()
                    chunk['Day'] = day
                    normalized_chunks.append(chunk)

            # Concatenate into a single normalized frame
            if normalized_chunks:
                df = pd.concat(normalized_chunks, ignore_index=True)
                
                # Reorder to bring 'Day' and common columns to the front
                common_names = self._clean_columns([_name_for_common(idx) for idx in common_cols_indices])
                leading_cols = ['Day'] + [name for name in common_names if name in df.columns]
                other_cols = [c for c in df.columns if c not in leading_cols]
                df = df[leading_cols + other_cols]
            else:
                # Fallback if normalization failed
                df = df.iloc[header_idx + 2:].copy()
                df.columns = self._clean_columns(df.columns)
        
        else:
            # --- Fallback: Standard Header ---
            # Assume first non-empty row is the header
            if not df.empty:
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
            best_score: Tuple[int, int] = (0, 0)  # (rows, cols)

            target_sheets = excel_file.sheet_names
            if sheet_name and sheet_name in target_sheets:
                target_sheets = [sheet_name]

            for sheet in target_sheets:
                # Load with header=None to manually detect layout
                df = excel_file.parse(sheet_name=sheet, dtype=str, header=None)
                
                # Process headers (detect hierarchy)
                df = self._process_dataframe(df)
                
                if df.empty:
                    continue

                df = df.fillna("")
                score = (len(df), len(df.columns))

                if sheet_name:
                    best_df = df
                    best_sheet = sheet
                    break

                if score > best_score:
                    best_score = score
                    best_df = df
                    best_sheet = sheet

            if best_df is None:
                raise Exception("No usable sheets found in the Excel file")

            data = best_df.astype(str).to_dict("records")
            suggested = self._detect_columns(list(best_df.columns))
            
            # Post-process: Split time ranges if detected
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
                raise Exception("Could not decode CSV file with any supported encoding")

            # Process headers (detect hierarchy)
            df = self._process_dataframe(df)
            df = df.fillna("")

            data = df.astype(str).to_dict("records")
            suggested = self._detect_columns(list(df.columns))
            
            # Post-process: Split time ranges if detected
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
        """Process time ranges in format START-END and clean data"""
        # Find time column
        time_col = None
        for col in columns:
            if 'time' in col.lower() or 'period' in col.lower():
                time_col = col
                break
        
        if not time_col:
            return data
        
        # Process each row
        processed_data = []
        for row in data:
            # Skip rows where ALL values are empty/nan (but keep rows with ANY non-empty value)
            non_empty_values = [v for v in row.values() if str(v).strip() and str(v).lower() not in ('nan', 'none', '')]
            if len(non_empty_values) == 0:
                continue
            
            # Clean the row
            cleaned_row = {}
            for key, value in row.items():
                val_str = str(value).strip()
                # Replace 'nan' with empty string
                if val_str.lower() in ['nan', 'none', '']:
                    cleaned_row[key] = ""
                else:
                    cleaned_row[key] = val_str
            
            # Split time range if present
            if time_col in cleaned_row and cleaned_row[time_col]:
                time_val = cleaned_row[time_col]
                # Check for time range pattern (e.g., "9:00-10:00", "09:00 - 10:00")
                time_range_pattern = r'(\d{1,2}:\d{2})\s*[-–]\s*(\d{1,2}:\d{2})'
                match = re.search(time_range_pattern, time_val)
                if match:
                    # Keep original format but could add start/end if needed
                    cleaned_row[time_col] = f"{match.group(1)}-{match.group(2)}"
            
            processed_data.append(cleaned_row)
        
        return processed_data

    @staticmethod
    def _detect_columns(columns: List[str]) -> Dict[str, Optional[str]]:
        patterns = {
            "date": [
                "date", "day", "weekday", "day name", "datum", "fecha"
            ],
            "time": [
                "time", "times", "period", "session", "slot", "start", "begin", "start time"
            ],
            "end_time": [
                "end", "finish", "until", "to", "end time", "finish time"
            ],
            "title": [
                "title", "event", "name", "subject", "course", "course title", "class", "module", "topic", "activity"
            ],
            "location": [
                "location", "room", "room no", "rm", "venue", "place", "hall", "building", "lab", "address", "classroom"
            ],
            "description": [
                "description", "notes", "details", "desc", "instructor", "teacher", "lecturer", "tutor"
            ],
        }
        mapping: Dict[str, Optional[str]] = {k: None for k in patterns.keys()}
        
        # Priority matching: Check for exact matches first
        for col in columns:
            col_l = col.lower().strip()
            # Exact matches for common timetable columns
            if col_l in ("day", "weekday") and not mapping["date"]:
                mapping["date"] = col
            elif col_l == "time" and not mapping["time"]:
                mapping["time"] = col
            elif col_l in ["course", "subject"] and not mapping["title"]:
                mapping["title"] = col
            elif col_l == "venue" and not mapping["location"]:
                mapping["location"] = col
        
        # Fuzzy matching for remaining columns
        for col in columns:
            col_l = col.lower()
            for key, keywords in patterns.items():
                if mapping[key]:
                    continue
                if any(kw in col_l for kw in keywords):
                    mapping[key] = col
                    break
        return mapping
