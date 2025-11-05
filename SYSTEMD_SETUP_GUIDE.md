# Systemd Service Setup Guide for Debian VPS

This guide will help you set up your scraping scripts as systemd services on your Debian VPS with automatic restart on failure.

## 📋 Overview

The systemd service setup provides:
- ✅ Automatic script restart on failure
- ✅ Configurable restart delay
- ✅ Boot-time auto-start option
- ✅ Centralized logging
- ✅ Easy management of multiple scripts
- ✅ Service status monitoring

## 🚀 Quick Start

### Step 1: Configure Which Scripts to Run

Edit `service_config.json` to specify which scripts you want to run:

```bash
nano service_config.json
```

**Important settings to update:**
- `python_path`: Path to Python (check with `which python3`)
- `working_directory`: Full path to your scrapping-app directory
- `user`: Your Linux username (check with `whoami`)
- `scripts_to_run`: Set `enabled: true` for scripts you want to run

Example configuration:
```json
{
  "python_path": "/usr/bin/python3",
  "working_directory": "/home/ubuntu/scrapping-app",
  "user": "ubuntu",
  "restart_on_failure": true,
  "restart_delay_seconds": 10,
  "scripts_to_run": [
    {
      "script_number": 1,
      "enabled": true,
      "description": "Script 1 - Pages 1 to 2,559"
    },
    {
      "script_number": 2,
      "enabled": true,
      "description": "Script 2 - Pages 2,560 to 5,118"
    },
    {
      "script_number": 3,
      "enabled": false,
      "description": "Script 3 - Disabled"
    }
  ]
}
```

### Step 2: Generate Service Files

Run the generator script on your VPS:

```bash
python3 generate_services.py
```

This will create service files in the `systemd_services/` directory.

### Step 3: Install Services on Debian

Follow these commands on your Debian VPS:

```bash
# 1. Create log directory
sudo mkdir -p /var/log/scraping
sudo chown $USER:$USER /var/log/scraping

# 2. Copy service files to systemd
sudo cp systemd_services/*.service /etc/systemd/system/

# 3. Reload systemd daemon
sudo systemctl daemon-reload

# 4. Enable services (to start on boot)
sudo systemctl enable scraping-script1.service
sudo systemctl enable scraping-script2.service
# ... repeat for all enabled scripts

# 5. Start services
sudo systemctl start scraping-script1.service
sudo systemctl start scraping-script2.service
# ... repeat for all enabled scripts
```

### Step 4: Verify Services are Running

```bash
# Check status of a specific service
sudo systemctl status scraping-script1.service

# Check if services are active
systemctl is-active scraping-script1.service

# Check logs
tail -f /var/log/scraping/script1.log
tail -f /var/log/scraping/script1.error.log
```

## 🛠️ Easy Management with manage_services.py

Use the management script for easier control:

```bash
# Make it executable
chmod +x manage_services.py

# Show status of all services
python3 manage_services.py status

# Start all services
python3 manage_services.py start

# Stop all services
python3 manage_services.py stop

# Restart all services
python3 manage_services.py restart

# Enable services to start on boot
python3 manage_services.py enable

# Disable services from starting on boot
python3 manage_services.py disable

# View logs for all services
python3 manage_services.py logs

# View logs for a specific script
python3 manage_services.py logs 1

# List all configured services
python3 manage_services.py list
```

## 📊 Monitoring and Logs

### View Real-time Logs

```bash
# Follow logs for a specific script
tail -f /var/log/scraping/script1.log

# Follow error logs
tail -f /var/log/scraping/script1.error.log

# View systemd journal
sudo journalctl -u scraping-script1.service -f

# View last 100 lines
sudo journalctl -u scraping-script1.service -n 100
```

### Check Service Status

```bash
# Detailed status
sudo systemctl status scraping-script1.service

# Check if service is enabled
systemctl is-enabled scraping-script1.service

# List all scraping services
systemctl list-units "scraping-script*"
```

## 🔄 Automatic Restart Configuration

The services are configured to automatically restart on failure:

- **Restart**: Always (whenever the script exits)
- **RestartSec**: 10 seconds (configurable in `service_config.json`)
- **StartLimitIntervalSec**: 0 (no limit on restart attempts)

### How It Works

1. If a script crashes or exits with an error, systemd will wait 10 seconds (configurable)
2. systemd will automatically restart the script
3. This continues indefinitely until you manually stop the service

### Adjust Restart Behavior

Edit `/etc/systemd/system/scraping-scriptX.service`:

```ini
[Service]
# Restart policy: always, on-failure, on-abnormal, on-abort, or never
Restart=always

# Wait 10 seconds before restarting
RestartSec=10

# Maximum time between restarts before reset (0 = no limit)
StartLimitIntervalSec=0

# Maximum restart attempts in StartLimitIntervalSec (empty = no limit)
StartLimitBurst=5
```

After editing, reload:
```bash
sudo systemctl daemon-reload
sudo systemctl restart scraping-script1.service
```

## 🎯 Common Operations

### Adding a New Script

1. Edit `service_config.json` - add the script with `enabled: true`
2. Run `python3 generate_services.py`
3. Copy new service file: `sudo cp systemd_services/scraping-scriptX.service /etc/systemd/system/`
4. Reload: `sudo systemctl daemon-reload`
5. Enable: `sudo systemctl enable scraping-scriptX.service`
6. Start: `sudo systemctl start scraping-scriptX.service`

### Disabling a Script

```bash
# Stop the service
sudo systemctl stop scraping-script1.service

# Disable from boot
sudo systemctl disable scraping-script1.service

# Or simply edit service_config.json and set enabled: false
```

### Updating a Script

When you update your Python script:

```bash
# Simply restart the service
sudo systemctl restart scraping-script1.service

# Or use the management script
python3 manage_services.py restart
```

### Removing a Service

```bash
# Stop and disable
sudo systemctl stop scraping-script1.service
sudo systemctl disable scraping-script1.service

# Remove the service file
sudo rm /etc/systemd/system/scraping-script1.service

# Reload daemon
sudo systemctl daemon-reload
```

## 🔍 Troubleshooting

### Service won't start

```bash
# Check detailed status
sudo systemctl status scraping-script1.service

# View full logs
sudo journalctl -u scraping-script1.service -n 100 --no-pager

# Check if Python path is correct
which python3

# Check if working directory exists
ls -la /path/to/your/scrapping-app

# Check if user has permissions
sudo -u your_username python3 /path/to/script1.py
```

### Service keeps restarting

Check the logs to see what error is occurring:
```bash
tail -f /var/log/scraping/script1.error.log
sudo journalctl -u scraping-script1.service -f
```

### Permission issues

```bash
# Ensure log directory has correct permissions
sudo chown -R $USER:$USER /var/log/scraping

# Check script file permissions
chmod +x scripts/script1/script1.py

# Run as the service user to test
sudo -u your_username python3 scripts/script1/script1.py
```

### Dependencies missing

```bash
# Install Python dependencies
cd /path/to/your/scrapping-app
pip3 install -r requirements.txt

# Or use virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Update service file to use venv python
# ExecStart=/path/to/venv/bin/python /path/to/script.py
```

## 📦 Using Virtual Environment (Recommended)

If you want to use a Python virtual environment:

1. Create virtual environment:
```bash
cd /path/to/scrapping-app
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Update `service_config.json`:
```json
{
  "python_path": "/path/to/scrapping-app/venv/bin/python"
}
```

3. Regenerate services:
```bash
python3 generate_services.py
sudo cp systemd_services/*.service /etc/systemd/system/
sudo systemctl daemon-reload
```

## 🔒 Security Considerations

### Run as non-root user

The services are configured to run as your user (not root), which is safer:

```ini
[Service]
User=your_username
```

### Resource Limits

Uncomment and adjust in the service file if needed:

```ini
[Service]
# Limit memory usage to 2GB
MemoryLimit=2G

# Limit CPU usage to 50%
CPUQuota=50%
```

### Log Rotation

Set up log rotation to prevent logs from filling disk:

```bash
sudo nano /etc/logrotate.d/scraping
```

Add:
```
/var/log/scraping/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0644 your_username your_username
}
```

## 📝 Summary of Files

- `service_config.json` - Configuration file where you specify which scripts to run
- `generate_services.py` - Generates systemd service files from config
- `manage_services.py` - Easy management of all services
- `systemd_services/` - Directory containing generated .service files
- `/etc/systemd/system/` - Where service files are installed on Linux
- `/var/log/scraping/` - Log directory for all scripts

## 🆘 Getting Help

If you encounter issues:

1. Check the logs: `python3 manage_services.py logs`
2. Check service status: `python3 manage_services.py status`
3. Test script manually: `python3 scripts/script1/script1.py`
4. Check systemd journal: `sudo journalctl -u scraping-script1.service -n 50`

## 🎉 Done!

Your scraping scripts are now running as systemd services with automatic restart on failure. They will:
- Start automatically on system boot (if enabled)
- Restart automatically if they crash
- Log all output to `/var/log/scraping/`
- Be easily manageable with `manage_services.py`

Happy scraping! 🚀
