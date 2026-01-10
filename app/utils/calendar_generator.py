"""
Calendar generation utility using icalendar library
"""
from icalendar import Calendar, Event as ICalEvent
from datetime import datetime, timedelta
from typing import List, Dict, Any
import pytz
from dateutil import parser as date_parser


class CalendarGenerator:
    """Generate iCalendar (.ics) files from event data"""
    
    def __init__(self):
        self.default_duration = timedelta(hours=1)
    
    def _merge_adjacent_events(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Merge adjacent time slots for the same course, date, and venue
        
        Args:
            events: List of event dictionaries
            
        Returns:
            List of merged events
        """
        if not events:
            return events
        
        import re
        
        def parse_time_range(time_str):
            """Parse time string to get start and end times"""
            if not time_str:
                return None
            
            # Handle formats like "8:30-9:20" or "8:30 - 9:20"
            range_match = re.match(r'(\d{1,2}:\d{2})\s*-\s*(\d{1,2}:\d{2})', time_str)
            if range_match:
                return {'start': range_match.group(1), 'end': range_match.group(2)}
            
            # If no range, just start time
            single_match = re.match(r'(\d{1,2}:\d{2})', time_str)
            if single_match:
                return {'start': single_match.group(1), 'end': None}
            
            return None
        
        # Group events by date, title, and location
        grouped = {}
        for idx, event in enumerate(events):
            key = f"{event.get('date')}|||{event.get('title')}|||{event.get('location', 'no-location')}"
            if key not in grouped:
                grouped[key] = []
            event_copy = event.copy()
            event_copy['_original_index'] = idx
            grouped[key].append(event_copy)
        
        merged_events = []
        
        for key, group in grouped.items():
            if len(group) == 1:
                # No merging needed
                del group[0]['_original_index']
                merged_events.append(group[0])
                continue
            
            # Parse times and sort by start time
            with_times = []
            for event in group:
                parsed = parse_time_range(event.get('time', ''))
                if parsed:
                    event['_parsed_time'] = parsed
                    with_times.append(event)
            
            with_times.sort(key=lambda e: e['_parsed_time']['start'].replace(':', ''))
            
            # Merge adjacent events
            i = 0
            while i < len(with_times):
                current = with_times[i].copy()
                end_time = current['_parsed_time']['end'] or current['_parsed_time']['start']
                
                # Look ahead for adjacent events
                j = i + 1
                while j < len(with_times):
                    next_event = with_times[j]
                    
                    # Check if next event starts where current ends
                    if end_time and next_event['_parsed_time']['start'] == end_time:
                        # Merge!
                        end_time = next_event['_parsed_time']['end'] or next_event['_parsed_time']['start']
                        j += 1
                    else:
                        break
                
                # Update the merged event
                if j > i + 1:
                    # We merged some events
                    current['time'] = f"{current['_parsed_time']['start']}-{end_time}"
                    print(f"Backend: Merged {j - i} time slots for {current.get('title')} on {current.get('date')} at {current.get('location', 'no location')}: {current['time']}")
                
                del current['_parsed_time']
                del current['_original_index']
                merged_events.append(current)
                
                i = j
        
        return merged_events
    
    def generate_ics(
        self,
        events: List[Dict[str, Any]],
        calendar_name: str = "My Timetable",
        timezone: str = "UTC"
    ) -> str:
        """
        Generate an iCalendar format string from event data
        
        Args:
            events: List of event dictionaries with keys:
                    - date: Date string
                    - time: Start time (optional)
                    - title: Event title
                    - location: Location (optional)
                    - description: Description (optional)
                    - end_time: End time (optional)
            calendar_name: Name of the calendar
            timezone: Timezone string (e.g., 'UTC', 'America/New_York')
            
        Returns:
            String containing the .ics file content
        """
        # Merge adjacent events before generating calendar
        events = self._merge_adjacent_events(events)
        
        # Create calendar
        cal = Calendar()
        cal.add('prodid', '-//Timetable Generator//EN')
        cal.add('version', '2.0')
        cal.add('x-wr-calname', calendar_name)
        cal.add('x-wr-timezone', timezone)
        
        # Get timezone object
        tz = pytz.timezone(timezone)
        
        # Add events
        for event_data in events:
            try:
                event = self._create_event(event_data, tz)
                cal.add_component(event)
            except Exception as e:
                # Skip invalid events but log the error
                print(f"Warning: Skipping event due to error: {str(e)}")
                continue
        
        return cal.to_ical().decode('utf-8')
    
    def _create_event(self, event_data: Dict[str, Any], tz) -> ICalEvent:
        """
        Create an iCalendar Event from event data
        """
        event = ICalEvent()
        
        # Parse time field - check if it contains a range (e.g., "9:00-10:00")
        time_str = event_data.get('time', '')
        start_time = None
        end_time_from_range = None
        
        if time_str and '-' in time_str:
            # Split time range
            parts = time_str.split('-')
            if len(parts) == 2:
                start_time = parts[0].strip()
                end_time_from_range = parts[1].strip()
        else:
            start_time = time_str
        
        # Parse date and start time
        start_dt = self._parse_datetime(
            event_data.get('date'),
            start_time,
            tz
        )
        
        # Determine end time (priority: time range > end_time field > 1 hour default)
        if end_time_from_range:
            # Use end time from time range
            end_dt = self._parse_datetime(
                event_data.get('date'),
                end_time_from_range,
                tz
            )
        elif event_data.get('end_time'):
            # Use explicit end_time field
            end_dt = self._parse_datetime(
                event_data.get('date'),
                event_data.get('end_time'),
                tz
            )
        else:
            # Default to 1 hour duration
            end_dt = start_dt + self.default_duration
        
        # Add required fields
        event.add('summary', event_data.get('title', 'Untitled Event'))
        event.add('dtstart', start_dt)
        event.add('dtend', end_dt)
        
        # Add optional fields
        if event_data.get('location'):
            event.add('location', event_data['location'])
        
        if event_data.get('description'):
            event.add('description', event_data['description'])
        
        # Add UID (unique identifier)
        uid = f"{start_dt.isoformat()}-{event_data.get('title', 'event')}@timetable-generator"
        event.add('uid', uid)
        
        # Add creation timestamp
        event.add('dtstamp', datetime.now(tz))
        
        # Add recurrence rule if specified
        recurring = event_data.get('recurring', 'none')
        if recurring and recurring != 'none':
            rrule_dict = {'FREQ': []}
            
            if recurring == 'weekly':
                # Repeat weekly on the same day of the week
                rrule_dict['FREQ'] = ['WEEKLY']
                weekday = start_dt.strftime('%a').upper()[:2]
                rrule_dict['BYDAY'] = [weekday]
            elif recurring == 'daily':
                # Daily, Monday through Friday
                rrule_dict['FREQ'] = ['WEEKLY']
                rrule_dict['BYDAY'] = ['MO', 'TU', 'WE', 'TH', 'FR']
            elif recurring in ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY']:
                # Specific weekday
                rrule_dict['FREQ'] = ['WEEKLY']
                weekday_map = {
                    'MONDAY': 'MO', 'TUESDAY': 'TU', 'WEDNESDAY': 'WE',
                    'THURSDAY': 'TH', 'FRIDAY': 'FR', 'SATURDAY': 'SA', 'SUNDAY': 'SU'
                }
                rrule_dict['BYDAY'] = [weekday_map[recurring]]
            
            if rrule_dict['FREQ']:
                event.add('rrule', rrule_dict)
        
        # Add reminder alarm (45 minutes before event by default)
        reminder_minutes = event_data.get('reminder_minutes', 45)
        if reminder_minutes and reminder_minutes > 0:
            from icalendar import Alarm
            alarm = Alarm()
            alarm.add('action', 'DISPLAY')
            alarm.add('description', f"Reminder: {event_data.get('title', 'Event')}")
            alarm.add('trigger', timedelta(minutes=-reminder_minutes))
            event.add_component(alarm)
        
        return event
    
    def _parse_datetime(self, date_str: str, time_str: str = None, tz=None) -> datetime:
        """
        Parse date and optional time strings into a datetime object
        
        Args:
            date_str: Date string (e.g., "2026-01-15", "15/01/2026", "Jan 15, 2026")
            time_str: Time string (e.g., "09:00", "9:00 AM", "14:30")
            tz: Timezone object
            
        Returns:
            Timezone-aware datetime object
        """
        # Parse date
        try:
            date_obj = date_parser.parse(date_str, fuzzy=True)
        except Exception as e:
            raise ValueError(f"Invalid date format: {date_str}")
        
        # Parse time if provided
        if time_str:
            try:
                # Extract time from string (handles "9:00 AM", "09:00", etc.)
                time_obj = date_parser.parse(time_str, fuzzy=True)
                date_obj = date_obj.replace(
                    hour=time_obj.hour,
                    minute=time_obj.minute,
                    second=0,
                    microsecond=0
                )
            except Exception:
                # If time parsing fails, use noon as default
                date_obj = date_obj.replace(hour=12, minute=0, second=0, microsecond=0)
        else:
            # No time specified, use noon
            date_obj = date_obj.replace(hour=12, minute=0, second=0, microsecond=0)
        
        # Make timezone-aware
        if tz:
            if date_obj.tzinfo is None:
                date_obj = tz.localize(date_obj)
            else:
                date_obj = date_obj.astimezone(tz)
        
        return date_obj
    
    def generate_summary(
        self,
        events: List[Dict[str, Any]],
        calendar_name: str = "My Timetable"
    ) -> Dict[str, Any]:
        """
        Generate a summary of the calendar without creating the file
        
        Returns:
            Dictionary with calendar statistics
        """
        if not events:
            return {
                "calendar_name": calendar_name,
                "total_events": 0,
                "date_range": None,
                "events_by_date": {}
            }
        
        # Count events by date
        events_by_date = {}
        all_dates = []
        
        for event in events:
            date = event.get('date', 'Unknown')
            if date not in events_by_date:
                events_by_date[date] = 0
            events_by_date[date] += 1
            
            try:
                parsed_date = date_parser.parse(date, fuzzy=True)
                all_dates.append(parsed_date)
            except:
                pass
        
        # Find date range
        date_range = None
        if all_dates:
            all_dates.sort()
            date_range = {
                "start": all_dates[0].strftime('%Y-%m-%d'),
                "end": all_dates[-1].strftime('%Y-%m-%d')
            }
        
        return {
            "calendar_name": calendar_name,
            "total_events": len(events),
            "date_range": date_range,
            "events_by_date": events_by_date
        }
