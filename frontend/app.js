// Configuration will be loaded from backend API
let API_BASE_URL = 'https://timetable-generator-183706276960.us-central1.run.app/api/v1'; // Temporary default (overridden by config loader)
let DEFAULT_CALENDAR_NAME = 'My Timetable'; // Temporary default
let DEFAULT_TIMEZONE = 'UTC'; // Temporary default

// State
let uploadedData = {
    uploadId: null,
    columns: [],
    previewData: [],
    mappedEvents: [],
    suggestedMapping: {},
    availableSheets: [],
    selectedSheet: null,
    lastFile: null,
    sourceType: null,
    sourceUrl: null,
    filename: null,
    baseDate: null,  // Store the user-selected base date
    selectedLevel: 'all',  // Track selected level filter
    searchQuery: ''  // Track search query
};

// Admin state
let adminState = {
    isLoggedIn: false,
    username: null,
    credentials: null
};

// Modal Functions
function openTipsModal() {
    const modal = document.getElementById('guide-modal');
    if (modal) {
        modal.classList.remove('hidden');
    }
}

function closeGuideModal() {
    const modal = document.getElementById('guide-modal');
    if (modal) {
        modal.classList.add('hidden');
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', async () => {
    // Load configuration from backend API first
    await loadConfig();
    
    // Update local variables from CONFIG
    API_BASE_URL = CONFIG.API_BASE_URL;
    DEFAULT_CALENDAR_NAME = CONFIG.DEFAULT_CALENDAR_NAME;
    DEFAULT_TIMEZONE = CONFIG.DEFAULT_TIMEZONE;
    
    console.log('[app.js] Configuration loaded:', { API_BASE_URL, DEFAULT_CALENDAR_NAME, DEFAULT_TIMEZONE });
    
    // Initialize calendar name from environment configuration
    const calendarNameInput = document.getElementById('calendar-name');
    if (calendarNameInput && DEFAULT_CALENDAR_NAME) {
        calendarNameInput.value = DEFAULT_CALENDAR_NAME;
        calendarNameInput.placeholder = DEFAULT_CALENDAR_NAME;
    }
    
    // Check if on admin page and restore credentials from sessionStorage
    if (window.location.pathname.includes('admin.html')) {
        const savedCredentials = sessionStorage.getItem('adminCredentials');
        const savedUsername = sessionStorage.getItem('adminUsername');
        if (savedCredentials && savedUsername) {
            adminState.isLoggedIn = true;
            adminState.credentials = savedCredentials;
            adminState.username = savedUsername;
        }
    }
    
    setupDragAndDrop();
    setupFileInput();
    setupUrlInput();
    fetchGallery();
});

// Drag and Drop
function setupDragAndDrop() {
    const uploadArea = document.getElementById('upload-area');
    if (!uploadArea) return;
    
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        uploadArea.addEventListener(eventName, () => {
            uploadArea.classList.add('drag-over');
        });
    });

    ['dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, () => {
            uploadArea.classList.remove('drag-over');
        });
    });

    uploadArea.addEventListener('drop', handleDrop);
    uploadArea.addEventListener('click', () => {
        const fileInput = document.getElementById('file-input');
        if (fileInput) fileInput.click();
    });
}

function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    
    if (files.length > 0) {
        handleFileUpload(files[0]);
    }
}

// File Input
function setupFileInput() {
    const fileInput = document.getElementById('file-input');
    if (!fileInput) return;

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileUpload(e.target.files[0]);
        }
    });
}

function setupUrlInput() {
    const urlInput = document.getElementById('url-input');
    if (!urlInput) return;

    urlInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            handleUrlUpload();
        }
    });
}

// File Upload Handler
async function handleFileUpload(file, sheetName = null) {
    // On public page, redirect to admin to upload
    if (!window.location.pathname.includes('admin.html')) {
        showStatus('info', 'Please use the admin panel to upload files');
        window.location.href = 'admin.html';
        return;
    }
    
    if (!adminState.isLoggedIn || !adminState.credentials) {
        showStatus('error', 'You must login as admin to upload files');
        return;
    }
    
    const allowedTypes = ['.pdf', '.xlsx', '.xls', '.csv'];
    const fileExt = '.' + file.name.split('.').pop().toLowerCase();
    
    if (!allowedTypes.includes(fileExt)) {
        showStatus('error', 'Unsupported file type. Please upload PDF, Excel, or CSV files.');
        return;
    }

    showLoading(true);
    showStatus('info', `Uploading ${file.name}...`);

    const formData = new FormData();
    formData.append('file', file);
    if (sheetName) {
        formData.append('sheet_name', sheetName);
    }

    try {
        const response = await fetch(`${API_BASE_URL}/upload/file`, {
            method: 'POST',
            headers: {
                'Authorization': `Basic ${adminState.credentials}`
            },
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Upload failed');
        }

        uploadedData.lastFile = file;
        processUploadResponse(data, {
            sourceType: getSourceTypeFromExt(fileExt),
            sourceUrl: null,
            filename: file.name
        });

    } catch (error) {
        showStatus('error', `Error: ${error.message}`);
    } finally {
        showLoading(false);
    }
}

async function handleUrlUpload(sheetName = null) {
    // On public page, redirect to admin to upload
    if (!window.location.pathname.includes('admin.html')) {
        showStatus('info', 'Please use the admin panel to upload from URL');
        window.location.href = 'admin.html';
        return;
    }
    
    if (!adminState.isLoggedIn || !adminState.credentials) {
        showStatus('error', 'You must login as admin to upload from URL');
        return;
    }
    
    const urlInput = document.getElementById('url-input');
    const url = urlInput ? urlInput.value.trim() : '';

    if (!url) {
        showStatus('error', 'Please paste a link to your timetable file.');
        return;
    }

    showLoading(true);
    showStatus('info', `Fetching ${url}...`);

    try {
        const payload = { url };
        if (sheetName) payload.sheet_name = sheetName;

        const response = await fetch(`${API_BASE_URL}/upload/url`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Basic ${adminState.credentials}`
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Fetch failed');
        }

        processUploadResponse(data, {
            sourceType: getSourceTypeFromExt(data.file_type),
            sourceUrl: url,
            filename: data.filename
        });

    } catch (error) {
        showStatus('error', `Error: ${error.message}`);
    } finally {
        showLoading(false);
    }
}

function processUploadResponse(data, meta = {}) {
    uploadedData.uploadId = data.upload_id;
    uploadedData.columns = data.detected_columns;
    uploadedData.previewData = data.preview_data;
    uploadedData.suggestedMapping = data.suggested_mapping || {};
    uploadedData.availableSheets = data.available_sheets || [];
    uploadedData.selectedSheet = data.sheet_used || null;
    if (meta.sourceType) uploadedData.sourceType = meta.sourceType;
    if (meta.filename) uploadedData.filename = meta.filename;
    if (meta.sourceUrl !== undefined) uploadedData.sourceUrl = meta.sourceUrl;

    showStatus('success', `✓ Successfully processed! Found ${data.preview_data.length} rows.`);
    
    // Debug logging
    console.log('Backend sent:', data.preview_data.length, 'rows');
    console.log('Columns:', uploadedData.columns);
    console.log('Sample rows:', uploadedData.previewData.slice(0, 5));

    setTimeout(() => {
        showMappingSection();
    }, 500);

    // Refresh gallery after successful upload
    fetchGallery();
}

function getSourceTypeFromExt(ext) {
    const normalized = (ext || '').toLowerCase();
    if (normalized === '.pdf') return 'pdf';
    if (normalized === '.csv') return 'csv';
    if (normalized === '.xls' || normalized === '.xlsx') return 'excel';
    return 'file';
}

// Show Status
function showStatus(type, message) {
    const statusEl = document.getElementById('upload-status');
    if (!statusEl) return; // Exit gracefully if status element doesn't exist
    
    statusEl.textContent = message;
    statusEl.className = 'status-message';
    
    if (type === 'success') statusEl.classList.add('status-success');
    if (type === 'error') statusEl.classList.add('status-error');
    if (type === 'info') statusEl.classList.add('status-info');
    if (type === 'warning') statusEl.classList.add('status-warning');
}

// Show Loading
function showLoading(show) {
    const loadingEl = document.getElementById('loading');
    if (loadingEl) loadingEl.classList.toggle('hidden', !show);
}

// Show Mapping Section
function showMappingSection() {
    const uploadSection = document.getElementById('upload-section');
    const mappingSection = document.getElementById('mapping-section');
    if (uploadSection) uploadSection.classList.add('hidden');
    if (!mappingSection) return; // Exit if mapping section doesn't exist
    mappingSection.classList.remove('hidden');
    renderSheetSelector();
    
    // Set default date to today
    const baseDateInput = document.getElementById('base-date-input');
    if (baseDateInput && !baseDateInput.value) {
        const today = new Date().toISOString().split('T')[0];
        baseDateInput.value = today;
    }
    
    // Populate column dropdowns
    const selects = [
        'date-column', 'time-column', 'title-column', 
        'location-column', 'end-time-column', 'description-column'
    ];
    
    selects.forEach(selectId => {
        const select = document.getElementById(selectId);
        if (!select) return; // Skip if select doesn't exist
        select.innerHTML = '<option value="">-- Select Column --</option>';
        
        uploadedData.columns.forEach(col => {
            const option = document.createElement('option');
            option.value = col;
            option.textContent = col;
            select.appendChild(option);
        });
    });

    // Auto-detect common column names
    autoDetectColumns();
}

// Sheet selector rendering
function renderSheetSelector() {
    const container = document.getElementById('sheet-selector');
    if (!container) return;

    const sheets = uploadedData.availableSheets || [];
    if (sheets.length <= 1) {
        container.classList.add('hidden');
        container.innerHTML = '';
        return;
    }

    container.classList.remove('hidden');
    const current = uploadedData.selectedSheet || sheets[0];
    const options = sheets.map(s => `<option value="${s}" ${s === current ? 'selected' : ''}>${s}</option>`).join('');
    container.innerHTML = `
        <div class="sheet-row">
            <label for="sheet-select">Choose sheet:</label>
            <select id="sheet-select" class="mapping-select">${options}</select>
            <button class="btn btn-secondary btn-small" onclick="changeSheet()">Load Sheet</button>
            <span class="sheet-hint">Currently using: ${uploadedData.selectedSheet || sheets[0]}</span>
        </div>
    `;
}

async function changeSheet() {
    const select = document.getElementById('sheet-select');
    if (!select) return;
    const sheet = select.value;
    if (!sheet) return;

    uploadedData.selectedSheet = sheet;
    showStatus('info', `Loading sheet "${sheet}"...`);
    showLoading(true);

    // Use the reparse endpoint if we have an upload_id
    if (uploadedData.uploadId) {
        try {
            const response = await fetch(`${API_BASE_URL}/upload/reparse/${uploadedData.uploadId}?sheet_name=${encodeURIComponent(sheet)}`, {
                method: 'POST'
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Failed to load sheet');
            }

            // Update with new sheet data
            processUploadResponse(data, {
                sourceType: uploadedData.sourceType,
                sourceUrl: uploadedData.sourceUrl,
                filename: uploadedData.filename
            });

        } catch (error) {
            showStatus('error', `Error loading sheet: ${error.message}`);
            // Fallback to re-upload if reparse fails
            if (uploadedData.lastFile) {
                handleFileUpload(uploadedData.lastFile, sheet);
            } else if (uploadedData.sourceUrl) {
                handleUrlUpload(sheet);
            }
        } finally {
            showLoading(false);
        }
    } else if (uploadedData.lastFile) {
        // Fallback for old uploads without upload_id
        handleFileUpload(uploadedData.lastFile, sheet);
        showLoading(false);
    } else if (uploadedData.sourceUrl) {
        // Fallback for URL uploads without upload_id
        handleUrlUpload(sheet);
        showLoading(false);
    } else {
        showStatus('error', 'No file or URL available to reload.');
        showLoading(false);
    }
}

// Auto-detect column names
function autoDetectColumns() {
    const columnMap = {
        'date-column': ['date', 'day', 'datum', 'fecha'],
        'time-column': ['time', 'start', 'begin', 'hora', 'zeit'],
        'title-column': ['title', 'event', 'name', 'subject', 'course', 'class'],
        'location-column': ['location', 'room', 'venue', 'place', 'ort'],
        'end-time-column': ['end', 'finish', 'end time', 'ende'],
        'description-column': ['description', 'notes', 'details', 'desc']
    };

    // First apply suggested mapping from backend if present
    const suggested = uploadedData.suggestedMapping || {};
    Object.entries({
        'date-column': suggested.date,
        'time-column': suggested.time,
        'title-column': suggested.title,
        'location-column': suggested.location,
        'end-time-column': suggested.end_time,
        'description-column': suggested.description,
    }).forEach(([selectId, colName]) => {
        if (colName && uploadedData.columns.includes(colName)) {
            document.getElementById(selectId).value = colName;
        }
    });

    // Fallback heuristic if any remain unset
    Object.keys(columnMap).forEach(selectId => {
        const selectEl = document.getElementById(selectId);
        if (selectEl.value) return;
        const keywords = columnMap[selectId];
        const matchedCol = uploadedData.columns.find(col => 
            keywords.some(keyword => col.toLowerCase().includes(keyword))
        );
        
        if (matchedCol) {
            selectEl.value = matchedCol;
        }
    });
}

// Date Calculation Helper Functions
function getNextWeekday(baseDate, targetDayName) {
    /**
     * Calculate the next occurrence of a weekday from a base date
     * @param {Date} baseDate - The starting date
     * @param {string} targetDayName - Day name (e.g., "Monday", "Tuesday")
     * @returns {string} - Date in YYYY-MM-DD format
     */
    const dayMap = {
        'sunday': 0, 'sun': 0,
        'monday': 1, 'mon': 1,
        'tuesday': 2, 'tue': 2, 'tues': 2,
        'wednesday': 3, 'wed': 3,
        'thursday': 4, 'thu': 4, 'thur': 4, 'thurs': 4,
        'friday': 5, 'fri': 5,
        'saturday': 6, 'sat': 6
    };
    
    const targetDay = dayMap[targetDayName.toLowerCase().trim()];
    if (targetDay === undefined) {
        return null; // Not a day name
    }
    
    const base = new Date(baseDate);
    const currentDay = base.getDay();
    
    // Calculate days until target day
    let daysToAdd = targetDay - currentDay;
    if (daysToAdd <= 0) {
        daysToAdd += 7; // Move to next week if same day or already passed
    }
    
    const resultDate = new Date(base);
    resultDate.setDate(base.getDate() + daysToAdd);
    
    // Format as YYYY-MM-DD
    return resultDate.toISOString().split('T')[0];
}

function isDayName(str) {
    /**
     * Check if a string is a day name
     */
    const dayNames = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday',
                      'sun', 'mon', 'tue', 'tues', 'wed', 'thu', 'thur', 'thurs', 'fri', 'sat'];
    return dayNames.includes(str.toLowerCase().trim());
}

function convertDayNamesToDates(events, baseDate) {
    /**
     * Convert day names to actual dates based on a base date
     * @param {Array} events - Array of event objects
     * @param {string} baseDate - Base date in YYYY-MM-DD format
     * @returns {Array} - Events with converted dates
     */
    if (!baseDate) {
        return events; // No conversion if no base date
    }
    
    return events.map(event => {
        const eventCopy = { ...event };
        
        // Check if date field contains a day name
        if (eventCopy.date && isDayName(eventCopy.date)) {
            const calculatedDate = getNextWeekday(baseDate, eventCopy.date);
            if (calculatedDate) {
                eventCopy.date = calculatedDate;
                eventCopy.originalDay = event.date; // Store original for reference
            }
        }
        
        return eventCopy;
    });
}

// Merge adjacent time slots for the same course
function mergeAdjacentEvents(events) {
    if (!events || events.length === 0) return events;
    
    // Parse time string to get start and end times
    function parseTimeRange(timeStr) {
        if (!timeStr) return null;
        
        // Handle formats like "8:30-9:20" or "8:30 - 9:20" or just "8:30"
        const rangeMatch = timeStr.match(/(\d{1,2}:\d{2})\s*-\s*(\d{1,2}:\d{2})/);
        if (rangeMatch) {
            return { start: rangeMatch[1], end: rangeMatch[2], original: timeStr };
        }
        
        // If no range, just start time
        const singleMatch = timeStr.match(/(\d{1,2}:\d{2})/);
        if (singleMatch) {
            return { start: singleMatch[1], end: null, original: timeStr };
        }
        
        return null;
    }
    
    // Group events by date, title, and location (venue)
    const grouped = {};
    events.forEach((event, index) => {
        const key = `${event.date}|||${event.title}|||${event.location || 'no-location'}`;
        if (!grouped[key]) {
            grouped[key] = [];
        }
        grouped[key].push({ ...event, _originalIndex: index });
    });
    
    const mergedEvents = [];
    
    Object.keys(grouped).forEach(key => {
        const group = grouped[key];
        
        if (group.length === 1) {
            // No merging needed
            mergedEvents.push(group[0]);
            return;
        }
        
        // Parse times and sort by start time
        const withTimes = group.map(event => {
            const parsed = parseTimeRange(event.time);
            return { ...event, _parsedTime: parsed };
        }).filter(e => e._parsedTime !== null);
        
        withTimes.sort((a, b) => {
            const aTime = a._parsedTime.start.replace(':', '');
            const bTime = b._parsedTime.start.replace(':', '');
            return parseInt(aTime) - parseInt(bTime);
        });
        
        // Merge adjacent events
        let i = 0;
        while (i < withTimes.length) {
            const current = withTimes[i];
            let merged = { ...current };
            let endTime = current._parsedTime.end || current._parsedTime.start;
            
            // Look ahead for adjacent events
            let j = i + 1;
            while (j < withTimes.length) {
                const next = withTimes[j];
                
                // Check if next event starts where current ends
                if (endTime && next._parsedTime.start === endTime) {
                    // Merge!
                    endTime = next._parsedTime.end || next._parsedTime.start;
                    j++;
                } else {
                    break;
                }
            }
            
            // Update the merged event
            if (j > i + 1) {
                // We merged some events
                merged.time = `${current._parsedTime.start}-${endTime}`;
                console.log(`Merged ${j - i} time slots for ${merged.title} on ${merged.date} at ${merged.location || 'no location'}: ${merged.time}`);
            }
            
            delete merged._parsedTime;
            delete merged._originalIndex;
            mergedEvents.push(merged);
            
            i = j;
        }
    });
    
    return mergedEvents;
}

// Apply Mapping
function applyMapping() {
    const dateCol = document.getElementById('date-column').value;
    const timeCol = document.getElementById('time-column').value;
    const titleCol = document.getElementById('title-column').value;
    
    // Get base date from input
    const baseDateInput = document.getElementById('base-date-input');
    uploadedData.baseDate = baseDateInput?.value || null;
    
    // Validation: Require Day, Time, and Course/Title (matching parser strategy)
    const missing = [];
    if (!dateCol) missing.push('Day/Date');
    if (!timeCol) missing.push('Time');
    if (!titleCol) missing.push('Course/Title');
    
    if (missing.length > 0) {
        alert(`Please select these required columns: ${missing.join(', ')}\n\nThese fields are required by the parser to generate valid calendar events.`);
        return;
    }

    const mapping = {
        date: dateCol,
        time: timeCol,
        title: titleCol,
        location: document.getElementById('location-column').value,
        end_time: document.getElementById('end-time-column').value,
        description: document.getElementById('description-column').value
    };

    // Map the data with validation (matching parser's _process_time_ranges logic)
    const allMappedEvents = uploadedData.previewData.map(row => {
        const event = {};
        
        Object.keys(mapping).forEach(key => {
            const colName = mapping[key];
            if (colName && row[colName] !== undefined) {
                const value = String(row[colName]).trim();
                // Skip empty or 'nan' values (matching parser cleanup)
                if (value && value.toLowerCase() !== 'nan' && value.toLowerCase() !== 'none') {
                    event[key] = value;
                }
            }
        });

        return { original: row, mapped: event };
    });

    // Debug: Log events that will be filtered out
    const filteredOut = allMappedEvents.filter(({ mapped }) => !mapped.date || !mapped.time || !mapped.title);
    if (filteredOut.length > 0) {
        console.log('Events being filtered out:', filteredOut.length);
        console.log('Reasons (first 10):');
        filteredOut.slice(0, 10).forEach((item, idx) => {
            const reasons = [];
            if (!item.mapped.date) reasons.push('missing date');
            if (!item.mapped.time) reasons.push('missing time');
            if (!item.mapped.title) reasons.push('missing title');
            console.log(`  ${idx + 1}. ${reasons.join(', ')} | Original:`, item.original, '| Mapped:', item.mapped);
        });
    }

    uploadedData.mappedEvents = allMappedEvents
        .filter(({ mapped }) => {
            // Keep only events with all required fields (Day, Time, Course)
            return mapped.date && mapped.time && mapped.title;
        })
        .map(({ mapped }) => mapped);

    if (uploadedData.mappedEvents.length === 0) {
        alert('No valid events found after filtering. Please check your column mapping and data quality.');
        return;
    }
    
    // Convert day names to actual dates if base date is provided
    if (uploadedData.baseDate) {
        // Check if any events have day names
        const hasDayNames = uploadedData.mappedEvents.some(e => isDayName(e.date));
        
        if (hasDayNames) {
            const originalCount = uploadedData.mappedEvents.length;
            uploadedData.mappedEvents = convertDayNamesToDates(uploadedData.mappedEvents, uploadedData.baseDate);
            
            // Count how many were converted
            const convertedCount = uploadedData.mappedEvents.filter(e => e.originalDay).length;
            if (convertedCount > 0) {
                showStatus('success', `✓ Converted ${convertedCount} day names to dates starting from ${uploadedData.baseDate}`);
            }
        } else {
            showStatus('info', `Base date set to ${uploadedData.baseDate}, but no day names found in date column.`);
        }
    }

    const filteredCount = uploadedData.previewData.length - uploadedData.mappedEvents.length;
    if (filteredCount > 0) {
        showStatus('info', `Filtered out ${filteredCount} incomplete row(s). ${uploadedData.mappedEvents.length} valid events ready.`);
    }
    
    // Merge adjacent time slots for the same course
    const beforeMergeCount = uploadedData.mappedEvents.length;
    uploadedData.mappedEvents = mergeAdjacentEvents(uploadedData.mappedEvents);
    const mergedCount = beforeMergeCount - uploadedData.mappedEvents.length;
    if (mergedCount > 0) {
        console.log(`Merged ${mergedCount} adjacent events`);
    }
    
    // Debug logging
    console.log('After mapping:', uploadedData.mappedEvents.length, 'events');
    console.log('Filtered out:', filteredCount, 'rows');
    console.log('Sample mapped events:', uploadedData.mappedEvents.slice(0, 5));

    showSelectionSection();
}

// Show Selection Section
function showSelectionSection() {
    document.getElementById('mapping-section').classList.add('hidden');
    document.getElementById('selection-section').classList.remove('hidden');
    
    renderEventsTable();
    updateEventCount();
}

// Extract level from course code (e.g., "DCIT203" -> 200, "DCIT322 (MK)" -> 300)
function extractLevelFromCourse(courseCode) {
    if (!courseCode) return null;
    
    // Match patterns like DCIT103, DCIT203, DCIT322 (MK), ABCD400, etc.
    // Look for letters followed by 3 digits, with optional text in brackets
    const match = courseCode.match(/[A-Z]+(\d{3})/);
    if (match) {
        const levelDigit = parseInt(match[1].charAt(0));
        // e.g., 203 -> level 2 -> 200, 322 -> level 3 -> 300, 415 -> level 4 -> 400
        return levelDigit * 100;
    }
    return null;
}

// Filter events by level
function filterByLevel(level) {
    uploadedData.selectedLevel = level;
    
    // Update active button
    document.querySelectorAll('.level-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    const selectedBtn = document.querySelector(`[data-level="${level}"]`);
    if (selectedBtn) {
        selectedBtn.classList.add('active');
    }
    
    // Re-render with filters
    filterAndSearchEvents();
}

// Search and filter events
function filterAndSearchEvents() {
    const searchQuery = document.getElementById('course-search').value.toLowerCase();
    uploadedData.searchQuery = searchQuery;
    
    const selectedLevel = uploadedData.selectedLevel;
    const rows = document.querySelectorAll('#table-body tr');
    let visibleCount = 0;
    
    rows.forEach((row, index) => {
        const event = uploadedData.mappedEvents[index];
        if (!event) return;
        
        // Check level filter
        let matchesLevel = true;
        if (selectedLevel !== 'all' && selectedLevel !== undefined) {
            const courseLevel = extractLevelFromCourse(event.title);
            // Only filter if we successfully extracted a level
            if (courseLevel !== null) {
                matchesLevel = courseLevel === selectedLevel;
            } else {
                // If we can't extract a level, show the event (don't filter it out)
                matchesLevel = true;
            }
        }
        
        // Check search query
        let matchesSearch = true;
        if (searchQuery) {
            const searchableText = [
                event.title || '',
                event.location || '',
                event.date || '',
                event.time || ''
            ].join(' ').toLowerCase();
            matchesSearch = searchableText.includes(searchQuery);
        }
        
        // Show or hide row
        if (matchesLevel && matchesSearch) {
            row.classList.remove('hidden-row');
            visibleCount++;
        } else {
            row.classList.add('hidden-row');
        }
    });
    
    // Update search results info
    const searchInfoEl = document.getElementById('search-results-info');
    if (searchQuery || (selectedLevel !== 'all' && selectedLevel !== undefined)) {
        searchInfoEl.classList.add('visible');
        const totalVisible = visibleCount;
        const total = uploadedData.mappedEvents.length;
        const filterInfo = [];
        if (searchQuery) filterInfo.push(`search: "${searchQuery}"`);
        if (selectedLevel !== 'all' && selectedLevel !== undefined) filterInfo.push(`level ${selectedLevel}`);
        searchInfoEl.textContent = `Showing ${totalVisible} of ${total} events (${filterInfo.join(', ')})`;
    } else {
        searchInfoEl.classList.remove('visible');
    }
}

// Render Events Table
function renderEventsTable() {
    const thead = document.getElementById('table-header');
    const tbody = document.getElementById('table-body');
    
    // Create header (matching parser column names: Day, Time, Course, Venue)
    const headers = ['Select', 'Day', 'Time', 'Course', 'Venue', 'Repeat'];
    thead.innerHTML = '<tr>' + 
        headers.map(h => `<th>${h}</th>`).join('') + 
        '</tr>';
    
    // Create rows with validation indicators
    tbody.innerHTML = uploadedData.mappedEvents.map((event, index) => {
        // Check if time format matches parser expectation (HH:MM or HH:MM-HH:MM)
        const hasValidTime = event.time && /\d{1,2}:\d{2}/.test(event.time);
        const isComplete = event.date && hasValidTime && event.title;
        const rowClass = isComplete ? '' : 'invalid-event';
        
        // Format date display - show original day name if it was converted
        let dateDisplay = event.date || '<span class="missing">-</span>';
        if (event.originalDay) {
            dateDisplay = `${event.date} <span class="converted-day">(${event.originalDay})</span>`;
        }
        
        // Extract level from course code
        const courseLevel = extractLevelFromCourse(event.title);
        const levelBadge = courseLevel ? `<span class="level-badge">${courseLevel}</span>` : '';
        
        const recurringValue = (uploadedData.recurringSettings && uploadedData.recurringSettings[index]) || 'none';

        return `
        <tr class="${rowClass}">
            <td>
                <input type="checkbox" 
                       class="event-checkbox" 
                       data-index="${index}" 
                       onchange="updateEventCount()">
            </td>
            <td>${dateDisplay}</td>
            <td>${event.time || '<span class="missing">-</span>'}</td>
            <td><strong>${levelBadge}${event.title || '<span class="missing">No course</span>'}</strong></td>
            <td>${event.location || '-'}</td>
            <td>
                <select class="recurring-select" data-index="${index}" onchange="updateRecurring(${index}, this.value)">
                    <option value="none" ${recurringValue === 'none' ? 'selected' : ''}>No repeat</option>
                    <option value="weekly" ${recurringValue === 'weekly' ? 'selected' : ''}>Weekly</option>
                    <option value="daily" ${recurringValue === 'daily' ? 'selected' : ''}>Daily (Mon-Fri)</option>
                    <option value="MONDAY" ${recurringValue === 'MONDAY' ? 'selected' : ''}>Every Monday</option>
                    <option value="TUESDAY" ${recurringValue === 'TUESDAY' ? 'selected' : ''}>Every Tuesday</option>
                    <option value="WEDNESDAY" ${recurringValue === 'WEDNESDAY' ? 'selected' : ''}>Every Wednesday</option>
                    <option value="THURSDAY" ${recurringValue === 'THURSDAY' ? 'selected' : ''}>Every Thursday</option>
                    <option value="FRIDAY" ${recurringValue === 'FRIDAY' ? 'selected' : ''}>Every Friday</option>
                    <option value="SATURDAY" ${recurringValue === 'SATURDAY' ? 'selected' : ''}>Every Saturday</option>
                    <option value="SUNDAY" ${recurringValue === 'SUNDAY' ? 'selected' : ''}>Every Sunday</option>
                </select>
            </td>
        </tr>
        `;
    }).join('');
    
    // Show data quality summary
    const completeCount = uploadedData.mappedEvents.filter(e => {
        const hasValidTime = e.time && /\d{1,2}:\d{2}/.test(e.time);
        return e.date && hasValidTime && e.title;
    }).length;
    
    if (completeCount < uploadedData.mappedEvents.length) {
        showStatus('warning', `${completeCount} of ${uploadedData.mappedEvents.length} events have complete data. Incomplete events highlighted in yellow.`);
    }
    
    // Initialize recurring settings
    if (!uploadedData.recurringSettings) {
        uploadedData.recurringSettings = uploadedData.mappedEvents.map(() => 'none');
    }
}

// Event Selection Functions
function selectAllEvents() {
    // Only select checkboxes in visible rows
    document.querySelectorAll('#table-body tr:not(.hidden-row) .event-checkbox').forEach(cb => {
        cb.checked = true;
    });
    updateEventCount();
}

function deselectAllEvents() {
    // Only deselect checkboxes in visible rows
    document.querySelectorAll('#table-body tr:not(.hidden-row) .event-checkbox').forEach(cb => {
        cb.checked = false;
    });
    updateEventCount();
}

function updateEventCount() {
    const checked = Array.from(document.querySelectorAll('.event-checkbox:checked'))
        .filter(cb => !cb.closest('tr').classList.contains('hidden-row')).length;
    document.getElementById('event-count').textContent = 
        `${checked} event${checked !== 1 ? 's' : ''} selected`;
}

function updateRecurring(index, value) {
    if (!uploadedData.recurringSettings) {
        uploadedData.recurringSettings = uploadedData.mappedEvents.map(() => 'none');
    }
    uploadedData.recurringSettings[index] = value;
}

function applyRecurringToAll(selectedValue) {
    // Handle custom day selection
    if (selectedValue === 'custom') {
        const customDaySelector = document.getElementById('custom-day-selector');
        const customDaySelect = document.getElementById('custom-recurring-day');
        
        // Show/hide the custom day selector
        if (customDaySelector.classList.contains('hidden')) {
            customDaySelector.classList.remove('hidden');
        } else {
            // If already visible and a day was selected, apply it
            if (customDaySelect.value) {
                applyRecurringPattern(customDaySelect.value);
            } else {
                // If no day selected yet, just keep the selector visible
                return;
            }
        }
        return;
    }
    
    // Hide custom day selector for other options
    const customDaySelector = document.getElementById('custom-day-selector');
    customDaySelector.classList.add('hidden');
    
    // Apply the selected pattern
    applyRecurringPattern(selectedValue);
}

function applyRecurringPattern(pattern) {
    if (!uploadedData.recurringSettings) {
        uploadedData.recurringSettings = uploadedData.mappedEvents.map(() => 'none');
    }
    
    // Update all dropdowns and settings
    document.querySelectorAll('.recurring-select').forEach((select, index) => {
        select.value = pattern;
        uploadedData.recurringSettings[index] = pattern;
    });
    
    showStatus('success', `Applied "${pattern}" to all events`);
}

// Generate Calendar
async function generateCalendar() {
    const checkboxes = Array.from(document.querySelectorAll('.event-checkbox:checked'))
        .filter(cb => !cb.closest('tr').classList.contains('hidden-row'));
    
    if (checkboxes.length === 0) {
        alert('Please select at least one event');
        return;
    }

    // Get reminder minutes from input
    const reminderMinutes = parseInt(document.getElementById('reminder-minutes').value) || 45;

    // Get selected events
    const selectedEvents = Array.from(checkboxes).map(cb => {
        const index = parseInt(cb.dataset.index);
        const event = { ...uploadedData.mappedEvents[index] };
        // Remove internal tracking field before sending to API
        delete event.originalDay;
        // Attach recurring preference for this event
        const recurring = uploadedData.recurringSettings?.[index] || 'none';
        event.recurring = recurring;
        // Add reminder_minutes to each event
        event.reminder_minutes = reminderMinutes;
        return event;
    });

    showLoading(true);

    try {
        const response = await fetch(`${API_BASE_URL}/calendar/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                events: selectedEvents,
                calendar_name: document.getElementById('calendar-name').value || 'My Timetable',
                timezone: document.getElementById('timezone').value || 'UTC'
            })
        });

        const data = await response.json();

        if (!response.ok) {
            // Handle validation errors from API
            if (data.detail && data.detail.validation_errors) {
                const errors = data.detail.validation_errors;
                const errorMsg = `Calendar validation failed:\n\n${errors.map(e => 
                    `• Event ${e.event_index} (${e.title}): ${e.errors.join(', ')}`
                ).join('\n')}\n\nPlease check the highlighted events and ensure they have valid Day, Time, and Course data.`;
                alert(errorMsg);
            } else {
                throw new Error(data.detail || 'Calendar generation failed');
            }
            return;
        }

        // Store events for download
        uploadedData.selectedEvents = selectedEvents;
        
        document.getElementById('event-total').textContent = selectedEvents.length;
        
        // Show success message with any warnings from API
        if (data.message) {
            showStatus('success', data.message);
        }
        
        showDownloadSection();
        renderCalendarPreview(selectedEvents);

    } catch (error) {
        showStatus('error', `Error: ${error.message}`);
    } finally {
        showLoading(false);
    }
}

// Render Calendar Preview
function renderCalendarPreview(events) {
    const previewContainer = document.getElementById('calendar-preview');
    
    if (!events || events.length === 0) {
        previewContainer.innerHTML = '<p class="preview-empty">No events to display</p>';
        return;
    }

    // Group events by date
    const eventsByDate = {};
    events.forEach(event => {
        const date = event.date || 'No Date';
        if (!eventsByDate[date]) {
            eventsByDate[date] = [];
        }
        eventsByDate[date].push(event);
    });

    // Sort dates
    const sortedDates = Object.keys(eventsByDate).sort();

    let html = '<div class="calendar-events-list">';
    
    sortedDates.forEach(date => {
        html += `<div class="calendar-date-group">`;
        html += `<div class="calendar-date-header">${formatDate(date)}</div>`;
        
        eventsByDate[date].forEach(event => {
            html += `
                <div class="calendar-event-item">
                    <div class="event-time">${event.time || ''}</div>
                    <div class="event-details">
                        <div class="event-title">${event.title || 'Untitled'}</div>
                        ${event.location ? `<div class="event-location">📍 ${event.location}</div>` : ''}
                        ${event.description ? `<div class="event-description">${event.description}</div>` : ''}
                    </div>
                </div>
            `;
        });
        
        html += `</div>`;
    });
    
    html += '</div>';
    previewContainer.innerHTML = html;
}

// Format date helper
function formatDate(dateStr) {
    if (!dateStr) return 'No Date';
    try {
        const date = new Date(dateStr);
        if (isNaN(date)) return dateStr;
        return date.toLocaleDateString('en-US', { weekday: 'short', year: 'numeric', month: 'short', day: 'numeric' });
    } catch {
        return dateStr;
    }
}

// Update reminder preview text
function updateReminderPreview() {
    const reminderMinutes = parseInt(document.getElementById('reminder-minutes').value) || 45;
    const previewEl = document.getElementById('reminder-preview');
    
    if (reminderMinutes === 0) {
        previewEl.textContent = 'No reminder';
    } else if (reminderMinutes === 1) {
        previewEl.textContent = '1 minute before';
    } else if (reminderMinutes < 60) {
        previewEl.textContent = `${reminderMinutes} minutes before`;
    } else {
        const hours = Math.floor(reminderMinutes / 60);
        const mins = reminderMinutes % 60;
        if (mins === 0) {
            previewEl.textContent = `${hours} hour${hours > 1 ? 's' : ''} before`;
        } else {
            previewEl.textContent = `${hours}h ${mins}m before`;
        }
    }
}

// Show Download Section
function showDownloadSection() {
    document.getElementById('selection-section').classList.add('hidden');
    document.getElementById('download-section').classList.remove('hidden');
}

// Download Calendar
async function downloadCalendar() {
    const calendarName = document.getElementById('calendar-name').value || 'My Timetable';
    const timezone = document.getElementById('timezone').value || 'UTC';

    showLoading(true);

    try {
        const response = await fetch(`${API_BASE_URL}/calendar/download`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                events: uploadedData.selectedEvents,
                calendar_name: calendarName,
                timezone: timezone
            })
        });

        if (!response.ok) {
            throw new Error('Download failed');
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${calendarName.replace(/\s+/g, '_')}.ics`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

    } catch (error) {
        alert(`Error: ${error.message}`);
    } finally {
        showLoading(false);
    }
}

// Navigation Functions
function resetUpload() {
    if (confirm('Are you sure? This will clear your current data.')) {
        location.reload();
    }
}

function goBackToMapping() {
    document.getElementById('selection-section').classList.add('hidden');
    document.getElementById('mapping-section').classList.remove('hidden');
}

function startOver() {
    if (confirm('Start over with a new file?')) {
        location.reload();
    }
}

// Subscription Functions
// Removed: Subscription functionality is no longer available

// Gallery: fetch and render saved uploads
async function fetchGallery() {
    try {
        const res = await fetch(`${API_BASE_URL}/upload/gallery`);
        const items = await res.json();
        renderGallery(items);
    } catch (e) {
        console.warn('Failed to load gallery:', e.message);
    }
}

function renderGallery(items) {
    const list = document.getElementById('gallery-list');
    if (!list) return;
    if (!items || items.length === 0) {
        list.innerHTML = '<p class="upload-hint">No saved timetables yet. Upload a file and save it with a name.</p>';
        return;
    }
    
    const isAdminPage = window.location.pathname.includes('admin.html');
    
    list.innerHTML = items.map(item => {
        const actionsHtml = isAdminPage 
            ? `
                <button class="btn btn-small btn-primary" onclick="useSavedUpload('${item.upload_id}')">Use</button>
                <button class="btn btn-small btn-secondary" onclick="renameUpload('${item.id}', '${item.name.replace(/'/g, "\\'")}')">Rename</button>
                <button class="btn btn-small btn-danger" onclick="deleteUpload('${item.id}')">Delete</button>
            `
            : `
                <button class="btn btn-small btn-primary" onclick="useSavedUpload('${item.upload_id}')">Use</button>
            `;
        
        return `
            <div class="gallery-card">
                <div><strong>${item.name}</strong></div>
                <div class="meta">${item.filename} • ${item.file_type}</div>
                <div class="actions">
                    ${actionsHtml}
                </div>
            </div>
        `;
    }).join('');
}

// Use saved upload: load preview via reparse endpoint
async function useSavedUpload(uploadId) {
    if (!uploadId) return;
    showStatus('info', 'Loading saved timetable...');
    showLoading(true);
    try {
        const response = await fetch(`${API_BASE_URL}/upload/reparse/${uploadId}`, { method: 'POST' });
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.detail || 'Failed to load saved upload');
        }
        // Use same flow as fresh upload
        processUploadResponse(data, {
            sourceType: getSourceTypeFromExt(data.file_type),
            filename: data.filename,
            sourceUrl: null
        });
    } catch (error) {
        showStatus('error', `Error: ${error.message}`);
    } finally {
        showLoading(false);
    }
}

// Delete an uploaded calendar
async function deleteUpload(savedId) {
    if (!savedId) return;
    
    if (!adminState.isLoggedIn || !adminState.credentials) {
        showStatus('error', 'You must be logged in as admin to delete calendars');
        return;
    }
    
    if (!confirm('Are you sure you want to delete this saved timetable?')) {
        return;
    }
    
    showLoading(true);
    try {
        const response = await fetch(`${API_BASE_URL}/upload/saved/${savedId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Basic ${adminState.credentials}`
            }
        });
        
        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.detail || 'Failed to delete calendar');
        }
        
        showStatus('success', 'Calendar deleted successfully');
        // Refresh the gallery
        fetchGallery();
    } catch (error) {
        showStatus('error', `Error: ${error.message}`);
    } finally {
        showLoading(false);
    }
}

// Rename an uploaded calendar
async function renameUpload(savedId, currentName) {
    if (!savedId) return;
    
    if (!adminState.isLoggedIn || !adminState.credentials) {
        showStatus('error', 'You must be logged in as admin to rename calendars');
        return;
    }
    
    const newName = prompt('Enter new name for this timetable:', currentName);
    if (!newName || newName.trim() === '' || newName === currentName) {
        return;
    }
    
    showLoading(true);
    try {
        const formData = new FormData();
        formData.append('new_name', newName.trim());
        
        const response = await fetch(`${API_BASE_URL}/upload/rename/${savedId}`, {
            method: 'PUT',
            headers: {
                'Authorization': `Basic ${adminState.credentials}`
            },
            body: formData
        });
        
        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.detail || 'Failed to rename calendar');
        }
        
        showStatus('success', 'Calendar renamed successfully');
        // Refresh the gallery
        fetchGallery();
    } catch (error) {
        showStatus('error', `Error: ${error.message}`);
    } finally {
        showLoading(false);
    }
}

// Save current upload to gallery
async function saveCurrentUpload() {
    const nameInput = document.getElementById('save-upload-name');
    const name = (nameInput?.value || '').trim();
    if (!uploadedData.uploadId) {
        showStatus('error', 'No current upload to save');
        return;
    }
    if (!name) {
        showStatus('error', 'Please enter a name to save');
        return;
    }
    if (!adminState.isLoggedIn || !adminState.credentials) {
        showStatus('error', 'You must be logged in as admin to save uploads');
        return;
    }
    try {
        const res = await fetch(`${API_BASE_URL}/upload/save`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Authorization': `Basic ${adminState.credentials}`
            },
            body: JSON.stringify({ upload_id: uploadedData.uploadId, name })
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Failed to save upload');
        showStatus('success', `Saved as "${data.name}"`);
        fetchGallery();
    } catch (e) {
        showStatus('error', `Error saving: ${e.message}`);
    }
}
