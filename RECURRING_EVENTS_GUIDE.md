# Recurring Events & Reminders Guide

## Overview
The timetable generator now supports recurring events and automatic reminders for each event.

## Features

### 1. Recurring Event Options
Each event can be configured with one of the following recurrence patterns:

- **No Repeat**: Single occurrence only
- **Weekly**: Repeats every week on the same day
- **Daily (Mon-Fri)**: Repeats Monday through Friday
- **Specific Weekday**: Repeats every specified day
  - Every Monday
  - Every Tuesday
  - Every Wednesday
  - Every Thursday
  - Every Friday
  - Every Saturday
  - Every Sunday

### 2. Automatic Reminders
- **Default**: 45 minutes before each event
- **Format**: VALARM component in iCalendar
- **Display**: Shows event title in reminder notification
- **Compatibility**: Works with all major calendar applications

## How to Use

### Setting Recurring Patterns (Individual Events)

1. **Upload & Map**: Upload your timetable file and complete column mapping
2. **Event Selection**: Navigate to the event selection grid
3. **Choose Pattern**: For each event, select a recurrence pattern from the dropdown:
   ```
   Select -> Date -> Time -> Title -> Location -> [Recurring Dropdown]
   ```
4. **Options Available**:
   - No Repeat (default)
   - Weekly
   - Every Monday through Sunday
   - Daily (Mon-Fri)

### Applying Patterns to All Events

Use the **"Apply Recurring to All"** button to set the same pattern for all events:

1. Click the button above the event table
2. Enter one of the following options:
   - `none` - No recurring
   - `weekly` - Weekly on same day
   - `MONDAY` through `SUNDAY` - Specific weekday
   - `daily` - Weekdays only
3. All dropdown menus will be updated automatically

### Example Use Cases

#### Weekly Class Schedule
```
Event: "Math 101"
Date: Monday, January 15, 2024
Time: 09:00
Recurring: "weekly"
Result: Event repeats every Monday at 9:00 AM
```

#### Specific Day Meetings
```
Event: "Team Standup"
Date: Tuesday, January 16, 2024
Time: 10:00
Recurring: "TUESDAY"
Result: Event repeats every Tuesday at 10:00 AM
```

#### Weekday Classes
```
Event: "Lab Work"
Date: Monday, January 15, 2024
Time: 14:00
Recurring: "daily"
Result: Event repeats Monday-Friday at 2:00 PM
```

## Technical Details

### iCalendar RRULE Format

The system generates standard iCalendar recurrence rules:

```ics
RRULE:FREQ=WEEKLY;BYDAY=MO          # Every Monday
RRULE:FREQ=WEEKLY;BYDAY=TU          # Every Tuesday
RRULE:FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR  # Weekdays
```

### Reminder Format

```ics
BEGIN:VALARM
ACTION:DISPLAY
DESCRIPTION:Reminder: Math 101
TRIGGER:-PT45M
END:VALARM
```

`-PT45M` means "45 minutes before event start"

## Calendar Application Support

### Google Calendar
- ✅ Recurring rules fully supported
- ✅ Reminders display as notifications
- ✅ Live subscription updates work seamlessly

### Apple Calendar (iOS/macOS)
- ✅ All recurrence patterns supported
- ✅ 45-minute reminders sync correctly
- ✅ Auto-updates with subscription links

### Outlook/Microsoft 365
- ✅ RRULE patterns recognized
- ✅ VALARM reminders supported
- ✅ Dynamic calendar sync enabled

### Other Applications
Most calendar applications that support iCalendar (RFC 5545) will handle:
- Recurring events (RRULE)
- Display-type alarms (VALARM)
- Calendar subscriptions (.ics URLs)

## API Changes

### Event Schema
```json
{
  "date": "2024-01-15",
  "time": "09:00",
  "title": "Math 101",
  "location": "Room 205",
  "recurring": "weekly",
  "reminder_minutes": 45
}
```

### New Fields
- `recurring` (string): Recurrence pattern
  - Valid values: `"none"`, `"weekly"`, `"daily"`, `"MONDAY"` - `"SUNDAY"`
- `reminder_minutes` (integer): Minutes before event for reminder
  - Default: 45

## Frontend Updates

### New UI Elements
1. **Recurring dropdown column** in event table
2. **"Apply Recurring to All"** button
3. **Info box** explaining recurring options
4. **Event count** shows total selected events

### State Management
- `uploadedData.recurringSettings`: Array storing each event's pattern
- Updated on dropdown change
- Sent to backend with calendar generation

## Testing Recommendations

### 1. Test Single Recurring Event
- Select one event
- Set to "weekly"
- Download calendar
- Import to your calendar app
- Verify it repeats weekly

### 2. Test Multiple Patterns
- Select 5 events
- Set different patterns (weekly, MONDAY, daily, none)
- Generate calendar
- Verify each pattern works correctly

### 3. Test Reminders
- Generate calendar with events
- Import to calendar app
- Check that reminders appear 45 minutes before

### 4. Test Subscription
- Create live subscription
- Add to calendar app
- Verify recurring events sync properly
- Check reminders persist

## Troubleshooting

### Recurring Events Not Showing Up
- **Check Pattern**: Ensure valid pattern selected (not "none")
- **Calendar App**: Some apps may take time to process RRULE
- **Date Range**: Calendar apps may limit how far ahead they show recurring events

### Reminders Not Working
- **App Permissions**: Ensure calendar app has notification permissions
- **System Settings**: Check device notification settings
- **Format Support**: Some older calendar apps may not support VALARM

### Subscription Not Updating
- **Refresh Interval**: Calendar apps cache subscriptions (typically 1-24 hours)
- **Manual Refresh**: Try manually refreshing the calendar in your app
- **URL Correct**: Verify subscription URL is complete and accessible

## Best Practices

1. **Use Weekly Pattern**: For class schedules that repeat on the same day each week
2. **Use Specific Days**: For meetings that always occur on specific weekdays
3. **Use Daily (Mon-Fri)**: For lab sessions or office hours on weekdays
4. **No Repeat**: For one-time events like exams or special lectures
5. **Test First**: Generate a test calendar with a few events before creating full schedule
6. **Document Patterns**: Keep notes on which recurring pattern works for which class type

## Future Enhancements

Potential features for future versions:
- Custom reminder times per event
- Multiple reminders per event
- End date for recurring events
- Interval customization (every 2 weeks, etc.)
- Exception dates (skip specific occurrences)
- Custom recurrence patterns (1st Monday of month, etc.)

## Support

For issues or questions:
1. Check this guide first
2. Review [COMPLETE_GUIDE.md](./COMPLETE_GUIDE.md) for full system documentation
3. Test with sample data to isolate the issue
4. Verify your calendar application supports iCalendar standards

---

**Version**: 2.0  
**Last Updated**: January 2024  
**Related Docs**: COMPLETE_GUIDE.md, SUBSCRIPTION_GUIDE.md, README.md
