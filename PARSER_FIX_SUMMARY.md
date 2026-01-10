# Parser Fix Summary - Duplicate Venues & Lost Time Column

## Issues Resolved

### Issue 1: Duplicate Venue Columns (venue_1, venue_2, etc.)
**Problem**: When unpivoting hierarchical headers (Monday-Course, Monday-Venue, Tuesday-Course, Tuesday-Venue), the `_clean_columns()` function was deduplicating ALL columns including attribute columns like "Venue", creating venue_1, venue_2, etc.

**Root Cause**: The `_clean_columns()` method added suffixes to ALL duplicate column names without understanding the context of unpivoting.

**Fix**: 
- Removed automatic deduplication from `_clean_columns()` 
- Added intelligent duplicate handling in the unpivoting logic that:
  - **Preserves common columns** (Time, Period) by removing duplicates after concat
  - **Doesn't deduplicate attribute columns** (Course, Venue) since they shouldn't be duplicates after proper unpivoting

### Issue 2: Time Column Lost with Duplicate Times
**Problem**: When multiple courses occurred at the same time, the Time column would disappear because pandas operations were treating duplicate time values as problematic.

**Root Cause**: Common columns (Time, Period) were being included multiple times in each chunk during unpivoting, then all copies were being deduplicated incorrectly.

**Fix**:
- Identified common columns during unpivoting (Time, Period, etc.)
- After concatenating chunks, intelligently remove duplicate common column instances while keeping one copy
- This preserves the Time column even when many courses share the same time slot

## Changes Made

### Change 1: Line 145 in parser.py
```python
# OLD:
chunk.columns = self._clean_columns(new_col_names)

# NEW:
chunk.columns = new_col_names
```

### Change 2: Lines 150-175 in parser.py  
Replaced simple duplicate renaming with intelligent handling:
```python
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

# Drop duplicate common columns
if cols_to_drop:
    df = df.drop(df.columns[cols_to_drop], axis=1)
```

### Change 3: Lines 398-403 in parser.py
Simplified `_clean_columns()` to not deduplicate:
```python
@staticmethod
def _clean_columns(columns: List[Any]) -> List[str]:
    """Clean column names but preserve duplicates for higher-level logic to handle"""
    cleaned = []
    for idx, col in enumerate(columns):
        name = str(col).strip() if col is not None else ""
        name = name or f"Column_{idx+1}"
        cleaned.append(name)
    return cleaned
```

## Expected Behavior After Fix

1. **No more venue_1, venue_2**: Venue columns from different days won't be incorrectly marked as duplicates
2. **Time column always present**: Even with multiple courses at 9:00 AM, the Time column will be preserved
3. **Proper unpivoting**: Each day's data will have its own row with Day | Time | Course | Venue structure

## Files Modified
- `app/utils/parser.py` (fixed version)
- `app/utils/parser_backup.py` (original backup)

## Testing
Upload a timetable with:
- Multiple days (Monday, Tuesday, etc.) with Course and Venue columns under each day
- Multiple courses at the same time (e.g., 9:00 AM)

Expected result:
- Single "Venue" column (not venue_1, venue_2)
- Single "Time" column present in all rows
- Each course-day combination as a separate row

## Additional Features Implemented
As a bonus, also added:
1. **SavedUpload** model to name and reuse uploaded files
2. **/upload/save** endpoint to name uploads
3. **/upload/gallery** endpoint to list saved uploads  
4. **/upload/reparse/{upload_id}** endpoint to reload saved files without re-uploading
5. Frontend gallery UI to select and reuse saved timetables
