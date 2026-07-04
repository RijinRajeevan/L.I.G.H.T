#!/bin/bash

# NYAYA-VAANI Ubuntu Installer Script
# This script automates the setup of the backend and frontend.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
echo "🛠️ Starting Installation in $SCRIPT_DIR..."

# 1. Update & Install System Dependencies
echo "📦 Installing system dependencies..."
sudo apt update
sudo apt install -y python3-venv python3-pip nodejs npm chromium-browser libmagic1 libgl1 x11-xserver-utils unclutter

# 2. Setup Backend
echo "🐍 Setting up Python Virtual Environment..."
cd "$SCRIPT_DIR/backend"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    echo "✅ Backend setup complete."
else
    echo "⏭️ venv already exists, skipping installation. (Delete the 'venv' folder if you want to force a reinstall)"
fi

# 3. Setup Frontend
echo "⚛️ Setting up Frontend..."
cd "$SCRIPT_DIR/frontend"
if [ ! -d "node_modules" ] || [ ! -d "dist" ]; then
    npm install
    npm run build
    echo "✅ Frontend setup complete."
else
    echo "⏭️ Frontend already built, skipping build. (Delete 'node_modules' or 'dist' if you want a fresh build)"
fi

# 4. Generate Autostart File
echo "🖥️ Generating Autostart entry..."
cat <<EOF > "$SCRIPT_DIR/nyaya-kiosk.desktop"
[Desktop Entry]
Type=Application
Name=Nyaya-Vaani Kiosk
Exec=$SCRIPT_DIR/start_kiosk.sh
X-GNOME-Autostart-enabled=true
NoDisplay=false
Hidden=false
Name[en_US]=Nyaya-Vaani Kiosk
Comment[en_US]=Starts the Civic AI Kiosk on Boot
EOF
chmod +x "$SCRIPT_DIR/start_kiosk.sh"

echo ""
echo "🎉 Installation Finished!"
echo "To enable Auto-Boot (Kiosk Mode):"
echo "1. Go to Ubuntu Settings -> Users -> Enable 'Automatic Login'"
echo "2. Run this command to add to autostart:"
echo "   mkdir -p ~/.config/autostart"
echo "   cp \"$SCRIPT_DIR/nyaya-kiosk.desktop\" ~/.config/autostart/"
echo "-------------------------------------------------------"
