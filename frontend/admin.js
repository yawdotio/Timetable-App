
// Admin Functions

// Restore admin credentials on admin page load
function restoreAdminSession() {
    const savedCredentials = sessionStorage.getItem('adminCredentials');
    const savedUsername = sessionStorage.getItem('adminUsername');
    if (savedCredentials && savedUsername) {
        adminState.isLoggedIn = true;
        adminState.credentials = savedCredentials;
        adminState.username = savedUsername;
        
        // Show admin panel
        if (document.getElementById('admin-panel-section')) {
            document.getElementById('admin-login-section').classList.add('hidden');
            document.getElementById('admin-panel-section').classList.remove('hidden');
            document.getElementById('logout-btn').style.display = 'block';
            loadAdminUploads();
            loadAdminCalendars();
        }
    }
}

function toggleAdminPanel() {
    const loginPanel = document.getElementById('admin-login-panel');
    loginPanel.classList.toggle('hidden');
}

async function adminLogin() {
    const username = document.getElementById('admin-username').value.trim();
    const password = document.getElementById('admin-password').value.trim();
    
    if (!username || !password) {
        showStatus('error', 'Please enter username and password');
        return;
    }
    
    try {
        const credentials = btoa(`${username}:${password}`);
        const response = await fetch(`${API_BASE_URL}/admin/login`, {
            method: 'POST',
            headers: {
                'Authorization': `Basic ${credentials}`
            }
        });
        
        if (!response.ok) {
            throw new Error('Invalid credentials');
        }
        
        const data = await response.json();
        adminState.isLoggedIn = true;
        adminState.username = username;
        adminState.credentials = credentials;
        
        // Store in sessionStorage so it persists on admin page
        sessionStorage.setItem('adminCredentials', credentials);
        sessionStorage.setItem('adminUsername', username);
        
        showStatus('success', `Welcome, ${username}!`);
        
        // If on admin page, show admin panel
        if (document.getElementById('admin-panel-section')) {
            document.getElementById('admin-login-section').classList.add('hidden');
            document.getElementById('admin-panel-section').classList.remove('hidden');
            document.getElementById('logout-btn').style.display = 'block';
            loadAdminUploads();
            loadAdminCalendars();
        }
        
    } catch (error) {
        showStatus('error', `Login failed: ${error.message}`);
    }
}

function adminLogout() {
    adminState.isLoggedIn = false;
    adminState.username = null;
    adminState.credentials = null;
    
    // Clear sessionStorage
    sessionStorage.removeItem('adminCredentials');
    sessionStorage.removeItem('adminUsername');
    
    // If on admin page, show login
    if (document.getElementById('admin-login-section')) {
        document.getElementById('admin-login-section').classList.remove('hidden');
        document.getElementById('admin-panel-section').classList.add('hidden');
        document.getElementById('logout-btn').style.display = 'none';
    }
    
    // Clear forms
    document.getElementById('admin-username').value = '';
    document.getElementById('admin-password').value = '';
    
    showStatus('success', 'Logged out');
}

function switchAdminTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.admin-tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.admin-tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(`${tabName}-tab`).classList.add('active');
    event.target.classList.add('active');
}

async function loadAdminUploads() {
    if (!adminState.isLoggedIn) return;
    
    try {
        const response = await fetch(`${API_BASE_URL}/admin/uploads`, {
            method: 'GET',
            headers: {
                'Authorization': `Basic ${adminState.credentials}`
            }
        });
        
        if (!response.ok) throw new Error('Failed to load uploads');
        
        const uploads = await response.json();
        const list = document.getElementById('admin-uploads-list');
        
        if (uploads.length === 0) {
            list.innerHTML = '<p class="upload-hint">No uploads yet</p>';
            return;
        }
        
        list.innerHTML = uploads.map(upload => `
            <div class="admin-list-item">
                <div class="admin-list-item-info">
                    <h5>${upload.filename}</h5>
                    <p>Type: ${upload.file_type} | Size: ${upload.file_size} bytes | Status: ${upload.status}</p>
                    <p>Events: ${upload.events_extracted || 0} | Created: ${upload.created_at || '-'}</p>
                </div>
                <div class="admin-list-item-actions">
                    <button class="btn btn-small btn-danger" onclick="adminDeleteUpload('${upload.id}')">Delete</button>
                </div>
            </div>
        `).join('');
        
    } catch (error) {
        showStatus('error', `Error loading uploads: ${error.message}`);
    }
}

async function loadAdminCalendars() {
    if (!adminState.isLoggedIn) return;
    
    try {
        const response = await fetch(`${API_BASE_URL}/admin/saved-calendars`, {
            method: 'GET',
            headers: {
                'Authorization': `Basic ${adminState.credentials}`
            }
        });
        
        if (!response.ok) throw new Error('Failed to load calendars');
        
        const calendars = await response.json();
        const list = document.getElementById('admin-calendars-list');
        
        if (calendars.length === 0) {
            list.innerHTML = '<p class="upload-hint">No saved calendars yet</p>';
            return;
        }
        
        list.innerHTML = calendars.map(cal => `
            <div class="admin-list-item">
                <div class="admin-list-item-info">
                    <h5>${cal.name}</h5>
                    <p>File: ${cal.filename} | Type: ${cal.file_type} | Created: ${cal.created_at || '-'}</p>
                </div>
                <div class="admin-list-item-actions">
                    <button class="btn btn-small btn-secondary" onclick="adminRenameCalendar('${cal.id}', '${cal.name.replace(/'/g, "\\'")}')">Rename</button>
                    <button class="btn btn-small btn-danger" onclick="adminDeleteCalendar('${cal.id}')">Delete</button>
                </div>
            </div>
        `).join('');
        
    } catch (error) {
        showStatus('error', `Error loading calendars: ${error.message}`);
    }
}

async function adminDeleteUpload(uploadId) {
    if (!adminState.isLoggedIn) return;
    
    if (!confirm('Are you sure you want to delete this upload?')) return;
    
    try {
        const response = await fetch(`${API_BASE_URL}/admin/upload/${uploadId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Basic ${adminState.credentials}`
            }
        });
        
        if (!response.ok) throw new Error('Failed to delete upload');
        
        showStatus('success', 'Upload deleted');
        loadAdminUploads();
        
    } catch (error) {
        showStatus('error', `Error: ${error.message}`);
    }
}

async function adminDeleteCalendar(calendarId) {
    if (!adminState.isLoggedIn) return;
    
    if (!confirm('Are you sure you want to delete this calendar?')) return;
    
    try {
        const response = await fetch(`${API_BASE_URL}/admin/saved-calendar/${calendarId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Basic ${adminState.credentials}`
            }
        });
        
        if (!response.ok) throw new Error('Failed to delete calendar');
        
        showStatus('success', 'Calendar deleted');
        loadAdminCalendars();
        
    } catch (error) {
        showStatus('error', `Error: ${error.message}`);
    }
}

async function adminRenameCalendar(calendarId, currentName) {
    if (!adminState.isLoggedIn) return;
    
    const newName = prompt('Enter new name:', currentName);
    if (!newName || newName === currentName) return;
    
    try {
        const formData = new FormData();
        formData.append('new_name', newName.trim());
        
        const response = await fetch(`${API_BASE_URL}/admin/saved-calendar/${calendarId}`, {
            method: 'PUT',
            headers: {
                'Authorization': `Basic ${adminState.credentials}`
            },
            body: formData
        });
        
        if (!response.ok) throw new Error('Failed to rename calendar');
        
        showStatus('success', 'Calendar renamed');
        loadAdminCalendars();
        
    } catch (error) {
        showStatus('error', `Error: ${error.message}`);
    }
}

// Update file upload to use admin credentials
async function uploadFile(file, sheetName = null) {
    if (!adminState.isLoggedIn) {
        showStatus('error', 'You must login as admin to upload files');
        toggleAdminPanel();
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    if (sheetName) {
        formData.append('sheet_name', sheetName);
    }

    try {
        showStatus('info', 'Uploading file...');
        const response = await fetch(`${API_BASE_URL}/upload/file`, {
            method: 'POST',
            headers: {
                'Authorization': `Basic ${adminState.credentials}`
            },
            body: formData
        });

        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.detail || 'Upload failed');
        }

        const data = await response.json();
        uploadedData.uploadId = data.upload_id;
        uploadedData.columns = data.detected_columns;
        uploadedData.previewData = data.preview_data;
        uploadedData.suggestedMapping = data.suggested_mapping;
        uploadedData.availableSheets = data.available_sheets;
        uploadedData.selectedSheet = data.sheet_used;
        uploadedData.sourceType = 'file';
        uploadedData.filename = data.filename;

        showStatus('success', data.message);
        showSection('mapping-section');
        renderEventsTable();

        // Handle multiple sheets if needed
        if (data.available_sheets && data.available_sheets.length > 1) {
            renderSheetSelector(data.available_sheets, data.sheet_used);
        }
    } catch (error) {
        showStatus('error', `Error: ${error.message}`);
    }
}

// Update URL upload to use admin credentials
async function uploadFromUrl(url, sheetName = null) {
    if (!adminState.isLoggedIn) {
        showStatus('error', 'You must login as admin to upload from URL');
        toggleAdminPanel();
        return;
    }
    
    try {
        showStatus('info', 'Fetching file from URL...');
        const response = await fetch(`${API_BASE_URL}/upload/url`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Basic ${adminState.credentials}`
            },
            body: JSON.stringify({ url, sheet_name: sheetName })
        });

        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.detail || 'Upload failed');
        }

        const data = await response.json();
        uploadedData.uploadId = data.upload_id;
        uploadedData.columns = data.detected_columns;
        uploadedData.previewData = data.preview_data;
        uploadedData.suggestedMapping = data.suggested_mapping;
        uploadedData.availableSheets = data.available_sheets;
        uploadedData.selectedSheet = data.sheet_used;
        uploadedData.sourceType = 'url';
        uploadedData.sourceUrl = url;
        uploadedData.filename = data.filename;

        showStatus('success', data.message);
        showSection('mapping-section');
        renderEventsTable();

        if (data.available_sheets && data.available_sheets.length > 1) {
            renderSheetSelector(data.available_sheets, data.sheet_used);
        }
    } catch (error) {
        showStatus('error', `Error: ${error.message}`);
    }
}
