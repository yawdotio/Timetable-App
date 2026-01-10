"""
Example usage scripts for testing the API
"""

# Example 1: Parse a sample timetable
sample_events = [
    {
        "date": "2026-01-20",
        "time": "09:00",
        "title": "Mathematics 101",
        "location": "Room A-201",
        "end_time": "10:30",
        "description": "Introduction to Calculus"
    },
    {
        "date": "2026-01-20",
        "time": "11:00",
        "title": "Physics Lab",
        "location": "Lab Building B",
        "end_time": "13:00",
        "description": "Mechanics Experiment"
    },
    {
        "date": "2026-01-21",
        "time": "14:00",
        "title": "Computer Science Seminar",
        "location": "Virtual - Zoom",
        "end_time": "16:00"
    },
    {
        "date": "2026-01-22",
        "time": "10:00",
        "title": "Chemistry Lecture",
        "location": "Room C-105",
        "end_time": "11:30",
        "description": "Organic Chemistry Basics"
    }
]

# Example 2: Column mapping for parsing rules
sample_parsing_rules = {
    "date_column": "Date",
    "time_column": "Start Time",
    "title_column": "Course Name",
    "location_column": "Venue",
    "description_column": "Notes",
    "end_time_column": "End Time",
    "date_format": "DD/MM/YYYY"
}

# Example 3: Subscription configuration
sample_subscription = {
    "name": "Spring 2026 Class Schedule",
    "description": "Automatically updated class timetable",
    "source_url": "https://university.edu/schedules/spring2026.xlsx",
    "source_type": "excel",
    "parsing_rules": sample_parsing_rules,
    "calendar_name": "University Classes",
    "timezone": "America/New_York"
}


def print_examples():
    """Print example usage"""
    print("=" * 60)
    print("TIMETABLE GENERATOR - EXAMPLE DATA")
    print("=" * 60)
    print("\n1. Sample Events:")
    print("-" * 60)
    for i, event in enumerate(sample_events, 1):
        print(f"\nEvent {i}:")
        print(f"  Date: {event['date']}")
        print(f"  Time: {event['time']} - {event.get('end_time', 'N/A')}")
        print(f"  Title: {event['title']}")
        print(f"  Location: {event['location']}")
    
    print("\n\n2. Parsing Rules:")
    print("-" * 60)
    for key, value in sample_parsing_rules.items():
        print(f"  {key}: {value}")
    
    print("\n\n3. API Usage Example:")
    print("-" * 60)
    print("""
    import requests
    
    # Generate calendar from events
    response = requests.post(
        "http://localhost:8000/api/v1/calendar/download",
        json={
            "events": sample_events,
            "calendar_name": "My Timetable",
            "timezone": "UTC"
        }
    )
    
    # Save the calendar file
    with open("timetable.ics", "wb") as f:
        f.write(response.content)
    
    print("Calendar saved as timetable.ics")
    """)
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    print_examples()
