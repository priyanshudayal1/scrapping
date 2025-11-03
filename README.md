# 🚀 Multi-Script Scraping System - Complete Guide

## 📋 Overview

This system divides 16.8M+ judgement PDFs into **66 independent scripts** distributed across **3-4 VPS instances** for parallel processing.

### Architecture

```
scrapping-app/
├── api+ui/                          # API Server & Web UI
│   ├── api_server_v2.py            # Enhanced API with script orchestration
│   ├── script_orchestrator.py      # Manages multiple script processes
│   ├── multi_script_dashboard.html # Main monitoring dashboard
│   └── .env                        # Instance-specific config (copied from .env.instanceN)
│
├── scripts/                         # 66 Individual Scraping Scripts
│   ├── script1/
│   │   ├── script1.py              # Scraping logic for pages 1-2,559
│   │   ├── script1_progress.json   # Progress tracking
│   │   ├── script1_timing.json     # Performance metrics
│   │   └── script1.log             # Execution logs
│   ├── script2/
│   │   └── ... (similar structure)
│   └── ... (66 scripts total)
│
├── .env.instance1                   # Config for Instance 1 (Scripts 1-17)
├── .env.instance2                   # Config for Instance 2 (Scripts 18-34)
├── .env.instance3                   # Config for Instance 3 (Scripts 35-51)
├── .env.instance4                   # Config for Instance 4 (Scripts 52-66)
├── start_instance1.ps1              # Start Instance 1
├── start_instance2.ps1              # Start Instance 2
├── start_instance3.ps1              # Start Instance 3
├── start_instance4.ps1              # Start Instance 4
└── instance_script_assignments.json # Script-to-instance mapping
```

---

## 📊 Distribution Summary

| Instance | Scripts | Pages | Est. Results |
|----------|---------|-------|--------------|
| **Instance 1** | 1-17 (17 scripts) | 1 to 43,503 | ~4.35M |
| **Instance 2** | 18-34 (17 scripts) | 43,504 to 87,006 | ~4.35M |
| **Instance 3** | 35-51 (17 scripts) | 87,007 to 130,509 | ~4.35M |
| **Instance 4** | 52-66 (15 scripts) | 130,510 to 168,867 | ~3.84M |

**Each script processes ~2,559 pages (~255,900 results)**

---

## 🛠️ Setup Instructions

### 1. Configure Environment Variables

Update AWS credentials in all `.env.instanceN` files:

```bash
# Edit .env.instance1, .env.instance2, .env.instance3, .env.instance4
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
```

### 2. Install Dependencies

```powershell
# Navigate to scrapping-app directory
cd scrapping-app

# Install required packages
pip install flask flask-cors boto3 python-dotenv selenium
```

### 3. Deploy to VPS Instances

**For each VPS:**

```bash
# Copy the entire scrapping-app directory to VPS
scp -r scrapping-app/ user@vps-ip:/path/to/

# SSH into VPS
ssh user@vps-ip

# Navigate to directory
cd /path/to/scrapping-app/

# Start the instance (use correct instance number)
./start_instance1.ps1  # For VPS 1
./start_instance2.ps1  # For VPS 2
./start_instance3.ps1  # For VPS 3
./start_instance4.ps1  # For VPS 4
```

---

## 🎮 API Endpoints

### Script Control

#### Start N Scripts Sequentially
```http
POST /api/scripts/start
Content-Type: application/json

{
  "num_scripts": 5,      # Number of scripts to start
  "delay": 2             # Delay between starts (seconds)
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Starting 5 scripts sequentially",
  "num_scripts": 5,
  "delay": 2
}
```

#### Start Single Script
```http
POST /api/scripts/start/<script_id>
```

**Example:**
```bash
curl -X POST http://35.226.62.197/api/scripts/start/1
```

#### Stop Single Script
```http
POST /api/scripts/stop/<script_id>
```

#### Stop All Scripts
```http
POST /api/scripts/stop-all
```

### Status & Monitoring

#### Get Overall Instance Status
```http
GET /api/status
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "instance_id": 1,
    "total_scripts": 17,
    "running_scripts": 5,
    "completed_scripts": 2,
    "error_scripts": 0,
    "total_files_downloaded": 125430,
    "total_pages": 43503,
    "completed_pages": 5000,
    "progress_percentage": 11.5,
    "scripts": [
      {
        "script_id": 1,
        "status": "running",
        "is_running": true,
        "current_page": 1523,
        "total_files_downloaded": 15230,
        "start_page": 1,
        "end_page": 2559,
        "total_pages": 2559
      },
      ...
    ]
  },
  "timestamp": "2025-10-30T12:34:56"
}
```

#### Get Single Script Status
```http
GET /api/scripts/<script_id>/status
```

#### Get Script Logs
```http
GET /api/scripts/<script_id>/logs?lines=50
```

#### Get Instance Information
```http
GET /api/instance/info
```

**Response:**
```json
{
  "status": "success",
  "instance_id": 1,
  "assigned_scripts": [1, 2, 3, ..., 17],
  "total_scripts": 17,
  "scripts_dir": "/path/to/scripts"
}
```

#### Health Check
```http
GET /api/health
```

---

## 🖥️ Web Dashboard

### Access Dashboard

**Local:**
```
http://35.226.62.197/
```

**VPS:**
```
http://YOUR_VPS_IP:5000/
```

### Dashboard Features

#### 1. **Control Panel**
- **Start N Scripts**: Enter number (1-66) and delay (seconds), then click "Start"
- **Stop All**: Emergency stop button for all running scripts
- **Delay Configuration**: Set pause time between sequential starts

#### 2. **Overall Statistics**
- Total Scripts (assigned to instance)
- Currently Running Scripts
- Completed Scripts
- Total Files Downloaded
- Overall Progress Percentage

#### 3. **Progress Bar**
- Visual representation of overall progress
- Shows completed pages vs. total pages

#### 4. **Filter & Search**
- Filter by status: All, Running, Not Started, Completed, Error
- Search by Script ID

#### 5. **Scripts Grid**
Each script card shows:
- **Script ID** and page range
- **Status badge** (Running/Not Started/Completed/Error)
- **Downloads count**
- **Current page**
- **Progress percentage**
- **Progress bar**
- **Control buttons**: Start, Stop, View Logs

#### 6. **Individual Script Controls**
- ▶️ **Start**: Launch individual script
- ⏹️ **Stop**: Terminate running script
- 📄 **Logs**: View recent log entries in new window

#### 7. **Auto-Refresh**
- Refreshes status every 5 seconds automatically
- Manual refresh button available

---

## 🚦 Usage Workflow

### Starting Scripts

#### Option 1: Start All Scripts at Once
```javascript
// In dashboard, set "Number of Scripts" to 17 (for instance 1)
// Click "Start" button
```

This will start all assigned scripts sequentially with 2-second delays.

#### Option 2: Start Gradually
```javascript
// Start first 3 scripts
num_scripts = 3

// Monitor their performance
// If stable, start 3 more
num_scripts = 3
```

#### Option 3: Start Specific Scripts
```javascript
// Click "Start" button on individual script cards
```

### Monitoring

1. **Overall Progress**: Check top statistics cards
2. **Individual Scripts**: Scroll through scripts grid
3. **Filter Active**: Select "Running" to see only active scripts
4. **Check Logs**: Click "Logs" button on any script card
5. **Search**: Type script ID to quickly find specific script

### Stopping Scripts

#### Stop Individual Script
```javascript
// Click "Stop" button on script card
// OR use API: POST /api/scripts/stop/5
```

#### Emergency Stop All
```javascript
// Click "Stop All Scripts" button in control panel
// Terminates all running scripts immediately
```

---

## 📈 Performance Optimization

### Recommended Sequential Startup

**For optimal performance:**

1. **Start 3-5 scripts** initially
2. **Wait 5-10 minutes**, monitor:
   - CPU usage
   - Memory consumption
   - Download speed
   - Error rate
3. **If stable**, start next batch
4. **Repeat** until all scripts running

### Resource Monitoring

**Check VPS resources:**
```bash
# CPU and Memory
htop

# Disk usage
df -h

# Network
iftop
```

**Optimal per VPS:**
- CPU: < 80% average
- Memory: < 75% used
- Disk I/O: < 70%
- Network: Stable connection

---

## 🔧 Troubleshooting

### Script Won't Start

**Check:**
1. Script file exists: `scripts/scriptN/scriptN.py`
2. Environment configured: `.env` file present
3. AWS credentials valid
4. No other script using same resources

**View logs:**
```bash
cat scripts/script1/script1.log
```

### Script Shows Error Status

**Actions:**
1. Click "Logs" button to view error details
2. Check `scriptN_progress.json` for error field
3. Fix issue (credentials, network, etc.)
4. Restart script

### High Resource Usage

**Solutions:**
1. Reduce number of concurrent scripts
2. Increase delay between starts (5-10 seconds)
3. Upgrade VPS resources
4. Check for memory leaks in logs

### Scripts Not Showing in Dashboard

**Check:**
1. API server running: `http://35.226.62.197/api/health`
2. Orchestrator initialized correctly
3. Instance ID matches environment
4. Browser console for JavaScript errors (F12)

---

## 📧 Email Notifications

The system sends emails for:
- ✅ **Script batch started** (when using "Start N Scripts")
- ❌ **Errors** in individual scripts
- ✅ **Completion** of individual scripts
- 🛑 **Manual stops** ("Stop All" button)

Configure in `.env.instanceN`:
```bash
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

---

## 📊 Progress Tracking Files

Each script maintains 3 files:

### 1. `scriptN_progress.json`
```json
{
  "script_id": 1,
  "start_page": 1,
  "end_page": 2559,
  "current_page": 523,
  "total_files_downloaded": 5230,
  "status": "running",
  "pages_completed": [1, 2, 3, ...],
  "failed_downloads": [],
  "yearly_counts": {"2020": 1234, "2021": 2345},
  "start_time": "2025-10-30T10:00:00",
  "last_updated": "2025-10-30T12:34:56"
}
```

### 2. `scriptN_timing.json`
```json
{
  "script_id": 1,
  "total_files_processed": 5230,
  "total_successful_downloads": 5200,
  "total_failed_downloads": 30,
  "average_time_per_file": 2.5,
  "session_start": "2025-10-30T10:00:00",
  "last_updated": "2025-10-30T12:34:56"
}
```

### 3. `scriptN.log`
Plain text log file with timestamped entries.

---

## 🔒 Security Best Practices

1. **Environment Variables**: Never commit `.env` files to git
2. **API Access**: Use firewall to restrict port 5000
3. **HTTPS**: Use nginx reverse proxy with SSL in production
4. **API Keys**: Implement API key authentication (optional)

---

## 📱 API Testing

### Using cURL

```bash
# Health check
curl http://35.226.62.197/api/health

# Get status
curl http://35.226.62.197/api/status

# Start 3 scripts
curl -X POST http://35.226.62.197/api/scripts/start \
  -H "Content-Type: application/json" \
  -d '{"num_scripts": 3, "delay": 2}'

# Start script 5
curl -X POST http://35.226.62.197/api/scripts/start/5

# Stop script 5
curl -X POST http://35.226.62.197/api/scripts/stop/5

# Stop all
curl -X POST http://35.226.62.197/api/scripts/stop-all

# Get script 1 status
curl http://35.226.62.197/api/scripts/1/status

# Get script 1 logs
curl http://35.226.62.197/api/scripts/1/logs?lines=20
```

### Using Python

```python
import requests

API_URL = "http://35.226.62.197/api"

# Start 5 scripts
response = requests.post(f"{API_URL}/scripts/start", json={
    "num_scripts": 5,
    "delay": 2
})
print(response.json())

# Get overall status
response = requests.get(f"{API_URL}/status")
status = response.json()
print(f"Running: {status['data']['running_scripts']}")
print(f"Downloaded: {status['data']['total_files_downloaded']}")
```

---

## 🎯 Quick Reference

### Instance Assignments

- **Instance 1 (VPS 1)**: Scripts 1-17
- **Instance 2 (VPS 2)**: Scripts 18-34
- **Instance 3 (VPS 3)**: Scripts 35-51
- **Instance 4 (VPS 4)**: Scripts 52-66

### Key Commands

```powershell
# Start instance
.\start_instance1.ps1

# View logs
cat api+ui\api_server.log
cat scripts\script1\script1.log

# Check running processes
ps aux | grep python

# Stop all
curl -X POST http://35.226.62.197/api/scripts/stop-all
```

### Important URLs

- **Dashboard**: `http://35.226.62.197/`
- **API Status**: `http://35.226.62.197/api/status`
- **Health Check**: `http://35.226.62.197/api/health`

---

## 📞 Support

For issues or questions:
1. Check logs: `scripts/scriptN/scriptN.log`
2. Verify API: `http://35.226.62.197/api/health`
3. Review configuration: `.env` files
4. Test individual script: `python scripts/script1/script1.py`

---

## ✅ Deployment Checklist

- [ ] Update AWS credentials in all `.env.instanceN` files
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Copy scrapping-app to all VPS instances
- [ ] Start each instance with correct startup script
- [ ] Verify API health on each instance
- [ ] Access dashboard and confirm script visibility
- [ ] Start 1-2 test scripts per instance
- [ ] Monitor performance for 10-15 minutes
- [ ] Gradually increase concurrent scripts
- [ ] Set up monitoring alerts (email notifications)
- [ ] Document VPS IPs and access credentials
- [ ] Configure firewall rules (port 5000)
- [ ] Set up automated backups of progress files

---

## 🚀 Next Steps

1. **Test locally** with 1-2 scripts
2. **Deploy to VPS 1** and test with 3-5 scripts
3. **Scale up** gradually on VPS 1
4. **Deploy to remaining VPS** instances
5. **Monitor and optimize** based on performance
6. **Full production** with all scripts running

---

**Created**: October 30, 2025
**System**: Multi-Script Distributed Scraping
**Total Scripts**: 66
**Instances**: 4
**Total PDFs**: 16.8M+
