#!/bin/bash
# Verification script for frontend configuration setup

echo "========================================"
echo "Frontend Configuration Verification"
echo "========================================"
echo ""

# Check if env-config.js exists
if [ -f "frontend/env-config.js" ]; then
    echo "✓ frontend/env-config.js exists"
    echo "  Content:"
    cat frontend/env-config.js | sed 's/^/    /'
else
    echo "✗ frontend/env-config.js not found"
    echo "  Run: bash setup-env.sh"
fi

echo ""

# Check if setup scripts exist
if [ -f "setup-env.sh" ]; then
    echo "✓ setup-env.sh found"
else
    echo "✗ setup-env.sh not found"
fi

if [ -f "setup-env.bat" ]; then
    echo "✓ setup-env.bat found"
else
    echo "✗ setup-env.bat not found"
fi

echo ""

# Check environment variables
echo "Current Environment Variables:"
echo "  API_BASE_URL=${API_BASE_URL:-<not set>}"
echo "  CALENDAR_NAME=${CALENDAR_NAME:-<not set>}"
echo "  TIMEZONE=${TIMEZONE:-<not set>}"

echo ""

# Check if app.js uses the variables
if grep -q "window.ENV_API_BASE_URL" frontend/app.js; then
    echo "✓ app.js uses ENV_API_BASE_URL"
else
    echo "✗ app.js does not use ENV_API_BASE_URL"
fi

if grep -q "window.ENV_CALENDAR_NAME" frontend/app.js; then
    echo "✓ app.js uses ENV_CALENDAR_NAME"
else
    echo "✗ app.js does not use ENV_CALENDAR_NAME"
fi

echo ""
echo "========================================"
echo "To generate env-config.js with your settings:"
echo "========================================"
echo ""
echo "Option 1: Using environment variables"
echo "  export API_BASE_URL=http://localhost:8000/api/v1"
echo "  export CALENDAR_NAME=\"My Calendar\""
echo "  export TIMEZONE=UTC"
echo "  bash setup-env.sh"
echo ""
echo "Option 2: Using .env.frontend file"
echo "  cp .env.frontend.example .env.frontend"
echo "  # Edit .env.frontend with your values"
echo "  bash setup-env.sh"
echo ""
