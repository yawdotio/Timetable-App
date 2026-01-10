#!/usr/bin/env bash
set -euo pipefail

# Generate frontend/env-config.js from environment variables (Vercel/Netlify)
# Required: API_BASE_URL (should include /api/v1)
# Optional: CALENDAR_NAME (default: My Timetable), TIMEZONE (default: UTC)

API_BASE_URL="${API_BASE_URL:-}"
CALENDAR_NAME="${CALENDAR_NAME:-My Timetable}"
TIMEZONE="${TIMEZONE:-UTC}"

if [[ -z "$API_BASE_URL" ]]; then
  echo "ERROR: API_BASE_URL environment variable is not set." >&2
  echo "Set it to your backend URL, e.g. https://<cloud-run>/api/v1" >&2
  exit 1
fi

mkdir -p frontend
cat > frontend/env-config.js <<EOF
// Auto-generated environment configuration
window.ENV_API_BASE_URL = '${API_BASE_URL}';
window.ENV_CALENDAR_NAME = '${CALENDAR_NAME}';
window.ENV_TIMEZONE = '${TIMEZONE}';
EOF

echo "✓ Wrote frontend/env-config.js"
echo "  API_BASE_URL=${API_BASE_URL}"
echo "  CALENDAR_NAME=${CALENDAR_NAME}"
echo "  TIMEZONE=${TIMEZONE}"
