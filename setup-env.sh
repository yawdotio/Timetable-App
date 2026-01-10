#!/bin/bash
# Frontend Environment Setup Script
# This script reads environment variables and injects them into the frontend

set -a  # Export all variables

# Load from .env file if it exists (for local development)
if [ -f ".env.frontend" ]; then
    source .env.frontend
fi

# Set defaults if not provided
API_BASE_URL="${API_BASE_URL:-http://localhost:8000/api/v1}"
CALENDAR_NAME="${CALENDAR_NAME:-My Timetable}"
TIMEZONE="${TIMEZONE:-UTC}"

set +a  # Stop exporting

# Create a JavaScript file with environment variables
cat > frontend/env-config.js << EOF
// Auto-generated environment configuration
window.ENV_API_BASE_URL = '${API_BASE_URL}';
window.ENV_CALENDAR_NAME = '${CALENDAR_NAME}';
window.ENV_TIMEZONE = '${TIMEZONE}';
EOF

echo "✓ Environment configuration updated:"
echo "  API_BASE_URL: ${API_BASE_URL}"
echo "  CALENDAR_NAME: ${CALENDAR_NAME}"
echo "  TIMEZONE: ${TIMEZONE}"
