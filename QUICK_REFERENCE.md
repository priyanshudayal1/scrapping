# Systemd Services - Quick Reference

## 🚀 Quick Setup (3 Steps)

### On your VPS:

```bash
# 1. Edit configuration (set which scripts to run)
nano service_config.json

# 2. Run installation script
chmod +x install_services.sh
./install_services.sh

# 3. Start all services
python3 manage_services.py start
```

## 📋 Common Commands

```bash
# Status of all services
python3 manage_services.py status

# Start all services
python3 manage_services.py start

# Stop all services
python3 manage_services.py stop

# Restart all services
python3 manage_services.py restart

# Enable services (start on boot)
python3 manage_services.py enable

# View logs
python3 manage_services.py logs

# View logs for specific script
python3 manage_services.py logs 1

# List configured services
python3 manage_services.py list
```

## 🔧 Manual systemd Commands

```bash
# Individual service control
sudo systemctl status scraping-script1.service
sudo systemctl start scraping-script1.service
sudo systemctl stop scraping-script1.service
sudo systemctl restart scraping-script1.service
sudo systemctl enable scraping-script1.service
sudo systemctl disable scraping-script1.service

# View logs
tail -f /var/log/scraping/script1.log
tail -f /var/log/scraping/script1.error.log
sudo journalctl -u scraping-script1.service -f

# List all scraping services
systemctl list-units "scraping-script*"
```

## 📝 service_config.json Format

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
      "enabled": false,
      "description": "Script 2 - Disabled"
    }
  ]
}
```

**Key Settings:**
- `enabled: true` - Service will be created and can be started
- `enabled: false` - Service will not be created
- `restart_delay_seconds` - Wait time before auto-restart (default: 10)

## 🔄 Adding/Removing Scripts

### Add a new script:
1. Edit `service_config.json` - add entry with `enabled: true`
2. Run `python3 generate_services.py`
3. Run `sudo cp systemd_services/scraping-scriptX.service /etc/systemd/system/`
4. Run `sudo systemctl daemon-reload`
5. Run `sudo systemctl start scraping-scriptX.service`

### Remove a script:
1. Run `sudo systemctl stop scraping-scriptX.service`
2. Run `sudo systemctl disable scraping-scriptX.service`
3. Edit `service_config.json` - set `enabled: false` or remove entry

## 🐛 Troubleshooting

### Service won't start:
```bash
# Check status
sudo systemctl status scraping-script1.service

# View detailed logs
sudo journalctl -u scraping-script1.service -n 50

# Check error log
tail -50 /var/log/scraping/script1.error.log

# Test manually
cd /path/to/scrapping-app
python3 scripts/script1/script1.py
```

### After code changes:
```bash
# Restart to apply changes
python3 manage_services.py restart
```

### Check if auto-restart is working:
```bash
# Kill the process - systemd should restart it
sudo pkill -f "script1.py"

# Wait 10 seconds, then check status
sleep 10
sudo systemctl status scraping-script1.service
```

## 📍 Important Paths

- **Config**: `service_config.json`
- **Generated services**: `systemd_services/*.service`
- **Installed services**: `/etc/systemd/system/scraping-script*.service`
- **Logs**: `/var/log/scraping/scriptX.log` and `scriptX.error.log`
- **Management**: `manage_services.py`
- **Generator**: `generate_services.py`

## ✨ Features

✅ Auto-restart on crash/error  
✅ Configurable restart delay  
✅ Start on system boot (optional)  
✅ Centralized logging  
✅ Easy configuration via JSON  
✅ Management script for all services  
✅ Works with virtual environments  

## 📖 Full Documentation

See `SYSTEMD_SETUP_GUIDE.md` for complete documentation.
