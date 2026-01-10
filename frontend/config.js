// Frontend configuration loader that works for both static hosting (e.g., Vercel)
// and when served alongside the backend.

let CONFIG = {
    API_BASE_URL: 'https://timetable-generator-183706276960.us-central1.run.app/api/v1',
    DEFAULT_CALENDAR_NAME: 'My Timetable',
    DEFAULT_TIMEZONE: 'UTC',
    MAX_UPLOAD_SIZE: 10485760, // 10MB in bytes
};

function applyEnvConfigIfAvailable() {
    if (typeof window === 'undefined') return false;

    const hasEnv = Boolean(window.ENV_API_BASE_URL);
    if (!hasEnv) return false;

    CONFIG = {
        API_BASE_URL: window.ENV_API_BASE_URL,
        DEFAULT_CALENDAR_NAME: window.ENV_CALENDAR_NAME || 'My Timetable',
        DEFAULT_TIMEZONE: window.ENV_TIMEZONE || 'UTC',
        MAX_UPLOAD_SIZE: window.ENV_MAX_UPLOAD_SIZE || 10485760,
    };
    console.log('[config] Loaded from env-config.js', CONFIG);
    return true;
}

function setDefaultConfig() {
    CONFIG = {
        API_BASE_URL: 'https://timetable-generator-183706276960.us-central1.run.app/api/v1',
        DEFAULT_CALENDAR_NAME: 'My Timetable',
        DEFAULT_TIMEZONE: 'UTC',
        MAX_UPLOAD_SIZE: 10485760,
    };
    console.log('[config] Using baked-in defaults', CONFIG);
}

// Fetch configuration from backend when env-config is not present
async function loadConfig() {
    // 1) Prefer build-time env (Vercel/Netlify) via env-config.js
    if (applyEnvConfigIfAvailable()) return CONFIG;

    // 2) Try runtime config endpoint (works when frontend shares domain with backend)
    try {
        const response = await fetch('/api/v1/config');
        if (response.ok) {
            const data = await response.json();
            CONFIG = {
                API_BASE_URL: data.api_base_url || CONFIG.API_BASE_URL,
                DEFAULT_CALENDAR_NAME: data.calendar_name || CONFIG.DEFAULT_CALENDAR_NAME,
                DEFAULT_TIMEZONE: data.timezone || CONFIG.DEFAULT_TIMEZONE,
                MAX_UPLOAD_SIZE: data.max_upload_size || CONFIG.MAX_UPLOAD_SIZE,
            };
            console.log('[config] Loaded from /api/v1/config', CONFIG);
            return CONFIG;
        }
        console.warn('[config] /api/v1/config returned non-200, using defaults');
    } catch (error) {
        console.warn('[config] Error loading /api/v1/config:', error, 'Using defaults');
    }

    // 3) Fall back to baked defaults
    setDefaultConfig();
    return CONFIG;
}

// Export for tests / Node usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { CONFIG, loadConfig, applyEnvConfigIfAvailable, setDefaultConfig };
}
