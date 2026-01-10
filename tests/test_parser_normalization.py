import pandas as pd

from app.utils.parser import FileParser


def _make_hierarchical_df():
    # Row 0: Days (None means common column)
    r0 = [None, 'Monday', 'Monday', 'Tuesday', 'Tuesday']
    # Row 1: Attributes
    r1 = ['Time', 'Course', 'Venue', 'Course', 'Venue']
    # Data rows
    r2 = ['08:00', 'Math', 'Room 1', 'Science', 'Room 2']
    r3 = ['10:00', 'Physics', 'Lab A', 'History', 'Hall B']
    data = [r0, r1, r2, r3]
    return pd.DataFrame(data)


def test_unpivot_hierarchical_headers():
    parser = FileParser()
    df = _make_hierarchical_df()

    out = parser._process_dataframe(df)

    # Expect normalized long format with explicit Day column
    assert 'Day' in out.columns
    assert set(['Time', 'Course', 'Venue']).issubset(set(out.columns))

    # For 2 data rows and 2 days -> 4 rows
    assert len(out) == 4

    # Days should include Monday and Tuesday
    assert set(out['Day']) == {'Monday', 'Tuesday'}

    # Check a couple of values exist after unpivot
    # One row for Monday at 08:00 Math / Room 1
    row = out[(out['Day'] == 'Monday') & (out['Time'] == '08:00')].iloc[0]
    assert row['Course'] == 'Math'
    assert row['Venue'] == 'Room 1'


def test_detect_columns_synonyms():
    columns = ['Day', 'Time', 'Course', 'Room No', 'Description']
    mapping = FileParser._detect_columns(columns)

    assert mapping['date'] == 'Day'
    assert mapping['time'] == 'Time'
    assert mapping['title'] == 'Course'
    assert mapping['location'] == 'Room No'


def test_time_range_normalization():
    parser = FileParser()
    columns = ['Day', 'Time', 'Course']
    data = [
        {'Day': 'Monday', 'Time': '9:00 - 10:00', 'Course': 'Math'},
        {'Day': 'Tuesday', 'Time': '14:30–16:00', 'Course': 'Science'},
        {'Day': 'Wednesday', 'Time': '11:00', 'Course': 'History'},
    ]

    processed = parser._process_time_ranges(data, columns)
    assert processed[0]['Time'] == '9:00-10:00'
    # en dash normalization handled by regex character class [-–]
    assert processed[1]['Time'] == '14:30-16:00'
    # single time remains unchanged
    assert processed[2]['Time'] == '11:00'
