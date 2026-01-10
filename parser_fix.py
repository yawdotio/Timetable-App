# Parser Fix: Prevent duplicate venue and preserve Time column with duplicates

# Issue 1: Duplicate venues (venue_1, venue_2, etc.)
# Cause: _clean_columns deduplicates ALL columns including those from unpivoting
# Fix: Don't deduplicate in _clean_columns, handle it intelligently in unpivoting logic

# Issue 2: Time column lost when there are duplicate times
# Cause: Common columns (Time) get duplicated during concat and then removed
# Fix: Identify common columns and remove duplicates while preserving one copy

# Changes needed:
# 1. Line 145: Remove self._clean_columns() call, use new_col_names directly
# 2. Lines 152-161: Replace duplicate handling logic to preserve common columns
# 3. Lines 366-381: Simplify _clean_columns to not deduplicate

print("Apply these changes to app/utils/parser.py:")
print()
print("=" * 80)
print("CHANGE 1: Line 145 - Don't call _clean_columns during chunk creation")
print("=" * 80)
print("OLD:")
print("    chunk.columns = self._clean_columns(new_col_names)")
print()
print("NEW:")
print("    chunk.columns = new_col_names")
print()

print("=" * 80)
print("CHANGE 2: Lines 150-161 - Smart duplicate handling for common vs attribute columns")
print("=" * 80)
print("OLD:")
print("""            # Concatenate into a single normalized frame: Day | common_cols | attributes
            if normalized_chunks:
                df = pd.concat(normalized_chunks, ignore_index=True)
                
                # Ensure no duplicate columns before reindexing
                if df.columns.duplicated().any():
                    # Rename duplicates
                    cols = pd.Series(df.columns)
                    for dup in cols[cols.duplicated()].unique():
                        cols[cols == dup] = [f"{dup}_{i}" if i != 0 else dup 
                                             for i in range(sum(cols == dup))]
                    df.columns = cols.tolist()""")
print()
print("NEW:")
print("""            # Concatenate into a single normalized frame: Day | common_cols | attributes
            if normalized_chunks:
                df = pd.concat(normalized_chunks, ignore_index=True)
                
                # Handle duplicate columns intelligently:
                # - Common columns (Time, Period) get duplicated during concat but contain same data
                #   -> Remove duplicates, keep only first occurrence
                # - Attribute columns (Course, Venue) are genuinely different per day
                #   -> These should NOT appear as duplicates if unpivot worked correctly
                if df.columns.duplicated().any():
                    # Identify which columns are common (Time, Period, etc.)
                    common_names = set()
                    for idx in common_cols_indices:
                        common_names.add(_name_for_common(idx))
                    
                    # Process duplicates
                    cols = pd.Series(df.columns)
                    cols_to_drop = []
                    
                    for dup in cols[cols.duplicated()].unique():
                        if dup in common_names:
                            # Common column: remove duplicates, keep first
                            dup_positions = cols[cols == dup].index.tolist()
                            cols_to_drop.extend(dup_positions[1:])  # Keep first only
                        # If it's NOT a common column appearing as duplicate, something went wrong
                        # but we'll leave it for now to debug
                    
                    # Drop duplicate common columns
                    if cols_to_drop:
                        df = df.drop(df.columns[cols_to_drop], axis=1)
                    
                    # Rebuild column names
                    df.columns = df.columns.tolist()""")
print()

print("=" * 80)
print("CHANGE 3: Lines 366-381 - Simplify _clean_columns (no deduplication)")
print("=" * 80)
print("OLD:")
print("""    @staticmethod
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
        return cleaned""")
print()
print("NEW:")
print("""    @staticmethod
    def _clean_columns(columns: List[Any]) -> List[str]:
        \"\"\"Clean column names but preserve duplicates for higher-level logic to handle\"\"\"
        cleaned = []
        for idx, col in enumerate(columns):
            name = str(col).strip() if col is not None else ""
            name = name or f"Column_{idx+1}"
            cleaned.append(name)
        return cleaned""")
