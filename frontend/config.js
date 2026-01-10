// Frontend Configuration
// Load from environment variables or use defaults

const CONFIG = {
    // API Configuration - can be overridden via environment variables
    API_BASE_URL: window.ENV_API_BASE_URL || 'http://localhost:8000/api/v1',
    
    // Frontend Configuration
    DEFAULT_CALENDAR_NAME: window.ENV_CALENDAR_NAME || 'My Timetable',
    DEFAULT_TIMEZONE: window.ENV_TIMEZONE || 'UTC',
    
    // UI Configuration
    MAX_UPLOAD_SIZE: 10485760, // 10MB in bytes
};

// Export for use in app.js
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CONFIG;
}
