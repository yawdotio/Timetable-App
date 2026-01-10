# Live Calendar Subscriptions - User Guide

## 🔗 What is a Live Subscription?

A live calendar subscription is a **dynamic URL** that calendar apps can subscribe to. Unlike a one-time download, subscriptions automatically update when your timetable changes.

## ✨ Benefits

**One-Time Download**:
- ✅ Simple and fast
- ✅ Works offline
- ❌ Doesn't update when timetable changes
- ❌ Need to re-download and re-import

**Live Subscription**:
- ✅ Auto-updates in your calendar app
- ✅ One URL works forever
- ✅ Changes reflected automatically
- ❌ Requires internet connection

## 📋 How to Use

### 1. Create a Subscription

1. Upload your timetable file
2. Map columns and select events
3. Click "Create Subscription" instead of "Download"
4. Fill in:
   - **Name**: e.g., "Fall 2026 Classes"
   - **Description**: Optional details
   - **Source URL**: (Optional) URL to auto-fetch updates from

5. Click "Create Subscription Link"
6. Copy your unique subscription URL

### 2. Add to Calendar App

#### Google Calendar
1. Open Google Calendar (web)
2. Click **+** next to "Other calendars" (left sidebar)
3. Select **"From URL"**
4. Paste your subscription link
5. Click **Add calendar**

Your calendar will update automatically every 24 hours.

#### Apple Calendar (macOS/iOS)
1. Open Calendar app
2. **File → New Calendar Subscription** (Mac)
   - Or: Settings → Calendar → Add Account → Other (iOS)
3. Paste your subscription link
4. Click **Subscribe**
5. Choose update frequency (recommended: Daily)

#### Microsoft Outlook
1. Open Outlook Calendar (web)
2. Click **Add calendar**
3. Select **Subscribe from web**
4. Paste your subscription link
5. Name your calendar
6. Click **Import**

Outlook checks for updates periodically.

### 3. Manage Subscriptions

Click **"📚 My Subscriptions"** in the header to:
- View all your subscriptions
- Copy subscription links
- Download .ics files
- Delete old subscriptions

## 🔄 How Updates Work

### Manual Mode (No Source URL)
- Your calendar displays the events you selected
- To update: Delete subscription and create a new one

### Auto-Update Mode (With Source URL)
- Provide a URL to an Excel/CSV file
- The server fetches from this URL on each calendar refresh
- Updates appear automatically in your calendar app

## 📝 Example Use Cases

### University Class Schedule
```
Name: "Spring 2026 Classes"
Source URL: https://university.edu/schedules/my-classes.xlsx
Description: "Computer Science major courses"
```
When the university updates the schedule, your calendar updates automatically!

### Work Shifts
```
Name: "Work Schedule"
Source URL: https://company.com/shifts/employee123.csv
Description: "My weekly work shifts"
```

### Conference Schedule
```
Name: "Tech Conference 2026"
Source URL: https://conference.com/schedule.xlsx
Description: "Sessions I'm attending"
```

## 🛠️ Technical Details

### Subscription URL Format
```
http://localhost:8000/api/v1/subscription/{subscription-id}/calendar.ics
```

### Update Frequency
- **Google Calendar**: Every 24 hours
- **Apple Calendar**: Based on your settings (hourly to weekly)
- **Outlook**: Every few hours

### Security
- Each subscription has a unique UUID
- No authentication required (webcal:// protocol)
- Anyone with the URL can access it

## ⚠️ Important Notes

1. **Don't lose your subscription URL** - Save it somewhere safe
2. **Calendar apps cache data** - Updates may take hours to appear
3. **Source URLs must be publicly accessible** - No authentication supported
4. **Delete old subscriptions** - They remain active until deleted

## 🆘 Troubleshooting

### Subscription not updating
- Check if your calendar app auto-refresh is enabled
- Try removing and re-adding the subscription
- Verify the source URL is accessible

### Events not showing
- Check timezone settings
- Verify column mapping was correct
- Ensure events have dates in the future

### "Invalid URL" error
- Make sure the API server is running
- Use the full URL including `http://`
- Check that the subscription ID is correct

## 🎯 Best Practices

1. **Use descriptive names** - "Math 101 T/Th" not "Calendar 1"
2. **Set appropriate timezones** - Match your location
3. **Test with one event first** - Verify it works before adding all events
4. **Keep source files accessible** - For auto-update mode
5. **Document your subscriptions** - Keep a list of what each URL is for

## 🔗 API Endpoints

For developers:

```bash
# Create subscription
POST /api/v1/subscription/

# Get subscription calendar
GET /api/v1/subscription/{id}/calendar.ics

# List subscriptions
GET /api/v1/subscription/

# Delete subscription
DELETE /api/v1/subscription/{id}
```

---

**Need help?** Check the API docs at http://localhost:8000/api/v1/docs
