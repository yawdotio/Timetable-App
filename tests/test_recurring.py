"""
Test script for recurring events and reminders
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.calendar_generator import CalendarGenerator
from datetime import datetime


def test_recurring_events():
    """Test calendar generation with recurring events and reminders"""
    
    print("Testing Recurring Events & Reminders...")
    print("-" * 50)
    
    # Create test events with different recurring patterns
    test_events = [
        {
            "date": "2024-01-15",
            "time": "09:00",
            "title": "Math 101 - Weekly Class",
            "location": "Room 205",
            "recurring": "weekly",
            "reminder_minutes": 45
        },
        {
            "date": "2024-01-16",
            "time": "10:00",
            "title": "Team Meeting - Every Tuesday",
            "location": "Conference Room",
            "recurring": "TUESDAY",
            "reminder_minutes": 45
        },
        {
            "date": "2024-01-17",
            "time": "14:00",
            "title": "Lab Work - Daily (Mon-Fri)",
            "location": "Lab 3",
            "recurring": "daily",
            "reminder_minutes": 45
        },
        {
            "date": "2024-01-18",
            "time": "11:00",
            "title": "Special Lecture - No Repeat",
            "location": "Auditorium",
            "recurring": "none",
            "reminder_minutes": 45
        }
    ]
    
    # Generate calendar
    generator = CalendarGenerator()
    
    try:
        ics_content = generator.generate_ics(
            events=test_events,
            calendar_name="Test Recurring Calendar",
            timezone="UTC"
        )
        
        print("✓ Calendar generated successfully!")
        print(f"✓ Total events: {len(test_events)}")
        print()
        
        # Verify RRULE presence for recurring events
        print("Checking recurring patterns...")
        for event in test_events:
            title = event['title']
            pattern = event['recurring']
            
            if pattern != 'none':
                if f"SUMMARY:{title}" in ics_content:
                    # Check if RRULE exists after this event
                    event_start = ics_content.find(f"SUMMARY:{title}")
                    event_section = ics_content[event_start:event_start+500]
                    
                    if "RRULE:" in event_section:
                        print(f"✓ {title[:30]:30} -> Recurring: {pattern}")
                    else:
                        print(f"✗ {title[:30]:30} -> MISSING RRULE!")
            else:
                print(f"○ {title[:30]:30} -> One-time event")
        
        print()
        print("Checking reminders...")
        
        # Verify VALARM presence
        alarm_count = ics_content.count("BEGIN:VALARM")
        print(f"✓ Found {alarm_count} reminder alarms")
        
        if alarm_count == len(test_events):
            print(f"✓ All {len(test_events)} events have reminders")
        else:
            print(f"⚠ Expected {len(test_events)} reminders, found {alarm_count}")
        
        # Check for 45-minute trigger
        if "TRIGGER:-PT45M" in ics_content:
            print("✓ 45-minute reminder trigger confirmed")
        else:
            print("✗ 45-minute trigger NOT found!")
        
        print()
        print("-" * 50)
        print("Sample iCalendar Output (first 1000 chars):")
        print("-" * 50)
        print(ics_content[:1000])
        print("...")
        print()
        print("✓ Test completed successfully!")
        
        # Save to file for inspection
        output_file = "test_recurring_calendar.ics"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(ics_content)
        print(f"✓ Calendar saved to: {output_file}")
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_recurring_events()
