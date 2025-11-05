#!/bin/bash
# Quick Installation Script for Debian VPS
# Run this script on your Debian VPS to set up everything

set -e

echo "=========================================="
echo "Scraping Services Installation Script"
echo "=========================================="
echo ""

# Get current directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "Error: This script must be run on Linux (Debian/Ubuntu)"
    exit 1
fi

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    echo "Install it with: sudo apt-get update && sudo apt-get install python3 python3-pip"
    exit 1
fi

echo "Current directory: $SCRIPT_DIR"
echo "Current user: $USER"
echo "Python path: $(which python3)"
echo ""

# Ask for confirmation
read -p "Is this the correct directory for your scrapping-app? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Please cd to your scrapping-app directory and run this script again"
    exit 1
fi

# Update service_config.json with correct paths
echo "Updating service_config.json with your system paths..."
python3 << 'EOF'
import json
import os
import sys

config_file = 'service_config.json'

# Get system info
python_path = sys.executable
working_dir = os.getcwd()
user = os.environ.get('USER', 'ubuntu')

# Load config
with open(config_file, 'r') as f:
    config = json.load(f)

# Update paths
config['python_path'] = python_path
config['working_directory'] = working_dir
config['user'] = user

# Save config
with open(config_file, 'w') as f:
    json.dump(config, f, indent=2)

print(f"✓ Updated python_path: {python_path}")
print(f"✓ Updated working_directory: {working_dir}")
print(f"✓ Updated user: {user}")
EOF

echo ""
echo "Checking Python dependencies..."
if [ ! -f "requirements.txt" ]; then
    echo "Warning: requirements.txt not found"
else
    echo "Installing Python packages..."
    pip3 install -r requirements.txt --user
fi

echo ""
echo "Generating systemd service files..."
python3 generate_services.py

if [ ! -d "systemd_services" ]; then
    echo "Error: Service files were not generated"
    exit 1
fi

SERVICE_COUNT=$(ls -1 systemd_services/*.service 2>/dev/null | wc -l)
if [ "$SERVICE_COUNT" -eq 0 ]; then
    echo "Error: No service files found"
    echo "Please edit service_config.json and set enabled:true for at least one script"
    exit 1
fi

echo ""
echo "Found $SERVICE_COUNT service file(s) to install"
echo ""

# Create log directory
echo "Creating log directory..."
sudo mkdir -p /var/log/scraping
sudo chown $USER:$USER /var/log/scraping
echo "✓ Created /var/log/scraping"

echo ""
echo "Installing service files to systemd..."
sudo cp systemd_services/*.service /etc/systemd/system/
echo "✓ Copied service files to /etc/systemd/system/"

echo ""
echo "Reloading systemd daemon..."
sudo systemctl daemon-reload
echo "✓ Systemd daemon reloaded"

echo ""
echo "=========================================="
echo "Installation Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Enable services (to start on boot):"
echo "   python3 manage_services.py enable"
echo ""
echo "2. Start services:"
echo "   python3 manage_services.py start"
echo ""
echo "3. Check status:"
echo "   python3 manage_services.py status"
echo ""
echo "4. View logs:"
echo "   python3 manage_services.py logs"
echo ""
echo "For more commands, run:"
echo "   python3 manage_services.py help"
echo ""
