#!/bin/bash

# NYAYA-VAANI Kiosk Startup Script
# Portable version for Ubuntu

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
echo "🚀 Starting NYAYA-VAANI Kiosk from $SCRIPT_DIR..."

# 1. Disable Screen Blanking / Power Saving
xset s off 2>/dev/null
xset -dpms 2>/dev/null
xset s noblank 2>/dev/null

# 2. Start Backend
echo "⏳ Starting Backend..."
cd "$SCRIPT_DIR/backend"
if [ ! -d "venv" ]; then
    echo "❌ venv not found! Please run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo "✅ Backend started (PID: $BACKEND_PID)"

# 3. Start Frontend (serve build)
echo "⏳ Starting Frontend..."
cd "$SCRIPT_DIR/frontend"
if [ ! -d "dist" ]; then
    echo "❌ 'dist' folder not found! Please run: npm install && npm run build"
    exit 1
fi
npx serve -s dist -l 5173 &
FRONTEND_PID=$!
echo "✅ Frontend started (PID: $FRONTEND_PID)"

# 4. Launch Browser in Kiosk Mode
echo "🌐 Launching Browser..."
sleep 5 # Wait for services
chromium-browser --kiosk --no-first-run --incognito --disable-restore-session-state "http://localhost:5173" || \
google-chrome --kiosk --no-first-run --incognito --disable-restore-session-state "http://localhost:5173"

# Cleanup on exit
echo "🛑 Shutting down..."
kill $BACKEND_PID
kill $FRONTEND_PID
