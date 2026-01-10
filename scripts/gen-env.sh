#!/usr/bin/env bash
set -euo pipefail

# Generate frontend/env-config.js from environment variables (Vercel/Netlify)
# Required: API_BASE_URL (should include /api/v1)
# Optional: CALENDAR_NAME (default: My Timetable), TIMEZONE (default: UTC)

echo "[BUILD] Generating frontend/env-config.js..."
echo "[BUILD] API_BASE_URL: ${API_BASE_URL:-<NOT SET>}"
echo "[BUILD] CALENDAR_NAME: ${CALENDAR_NAME:-<NOT SET>}"
echo "[BUILD] TIMEZONE: ${TIMEZONE:-<NOT SET>}"

API_BASE_URL="${API_BASE_URL:-}"
CALENDAR_NAME="${CALENDAR_NAME:-My Timetable}"
TIMEZONE="${TIMEZONE:-UTC}"

if [[ -z "$API_BASE_URL" ]]; then
  echo "[ERROR] API_BASE_URL environment variable is not set." >&2
  echo "[ERROR] Set it in your Vercel/Netlify project settings." >&2
  echo "[ERROR] Example: https://timetable-generator-xxx.run.app/api/v1" >&2
  exit 1
fi

mkdir -p frontend
cat > frontend/env-config.js <<EOF
// Auto-generated environment configuration
window.ENV_API_BASE_URL = '${API_BASE_URL}';
window.ENV_CALENDAR_NAME = '${CALENDAR_NAME}';
window.ENV_TIMEZONE = '${TIMEZONE}';
EOF

echo "[BUILD] ✓ Successfully wrote frontend/env-config.js"
ls -la frontend/env-config.js
echo "[BUILD] File contents:"
cat frontend/env-config.js
