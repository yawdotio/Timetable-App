#!/bin/bash

echo "========================================"
echo "Timetable Generator - Quick Start"
echo "========================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create virtual environment"
        exit 1
    fi
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo ""
echo "Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies"
    exit 1
fi

echo ""
echo "Setting up frontend environment configuration..."
bash setup-env.sh
if [ $? -ne 0 ]; then
    echo "Warning: Failed to setup environment (non-critical)"
fi

echo ""
echo "Setting up environment..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "Created .env file from .env.example"
fi

echo ""
echo "Initializing database..."
python init_db.py
if [ $? -ne 0 ]; then
    echo "Error: Failed to initialize database"
    exit 1
fi

echo ""
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "Starting the server..."
echo "API will be available at: http://localhost:8000"
echo "Interactive docs at: http://localhost:8000/api/v1/docs"
echo ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
