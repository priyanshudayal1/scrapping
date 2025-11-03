# 🚀 Quick Start Guide - Multi-Script Scraping System

## ⚡ 5-Minute Setup

### 1️⃣ Install Dependencies
```powershell
cd scrapping-app
pip install -r requirements.txt
```

### 2️⃣ Configure AWS Credentials
Edit `.env.instance1` (or instance2, 3, 4):
```bash
AWS_ACCESS_KEY_ID=your_actual_key_here
AWS_SECRET_ACCESS_KEY=your_actual_secret_here
```

### 3️⃣ Start Instance
```powershell
# For Instance 1
.\start_instance1.ps1

# For Instance 2
.\start_instance2.ps1

# And so on...
```

### 4️⃣ Open Dashboard
```
http://35.226.62.197/
```

### 5️⃣ Start Scripts
In the dashboard:
1. Enter **number of scripts** (e.g., 3)
2. Set **delay** (2-5 seconds recommended)
3. Click **▶️ Start** button

---

## 📊 What Happens?

### Instance 1
- **Manages**: Scripts 1-17
- **Pages**: 1 to 43,503
- **Results**: ~4.35M PDFs

### Instance 2
- **Manages**: Scripts 18-34
- **Pages**: 43,504 to 87,006
- **Results**: ~4.35M PDFs

### Instance 3
- **Manages**: Scripts 35-51
- **Pages**: 87,007 to 130,509
- **Results**: ~4.35M PDFs

### Instance 4
- **Manages**: Scripts 52-66
- **Pages**: 130,510 to 168,867
- **Results**: ~3.84M PDFs

---

## 🎮 Dashboard Controls

### Start Scripts
```
Number of Scripts: [5]  [Delay: 2 seconds]  [▶️ Start]
```
- Starts 5 scripts, one every 2 seconds

### Individual Control
Each script card has:
- ▶️ **Start** - Launch this script
- ⏹️ **Stop** - Terminate this script
- 📄 **Logs** - View execution logs

### Emergency Stop
```
[⏹️ Stop All Scripts]
```
- Immediately terminates all running scripts

---

## 📈 Monitoring

### Real-time Stats
- **Total Scripts**: How many assigned to this instance
- **Running**: Currently active scripts
- **Completed**: Finished scripts
- **Downloaded**: Total PDFs processed
- **Progress**: Overall completion percentage

### Filter & Search
```
[All Scripts ▼]  [Search Script ID...]  [🔄 Refresh]
```
- Filter by status (Running, Completed, Error)
- Search by script number
- Manual refresh

---

## 🔧 API Usage

### Start 5 Scripts
```bash
curl -X POST http://35.226.62.197/api/scripts/start \
  -H "Content-Type: application/json" \
  -d '{"num_scripts": 5, "delay": 2}'
```

### Check Status
```bash
curl http://35.226.62.197/api/status
```

### Stop All
```bash
curl -X POST http://35.226.62.197/api/scripts/stop-all
```

---

## 📂 File Structure

```
scrapping-app/
├── api+ui/                    # Web server & API
│   ├── api_server_v2.py      # Main API
│   ├── script_orchestrator.py # Script manager
│   └── multi_script_dashboard.html
│
├── scripts/                   # 66 Scripts
│   ├── script1/
│   │   ├── script1.py        # Scraping code
│   │   ├── script1_progress.json  # Progress
│   │   └── script1.log       # Logs
│   └── ... (66 total)
│
├── .env.instance1            # Config for VPS 1
├── start_instance1.ps1       # Startup script
└── README.md                 # Full documentation
```

---

## ✅ Pre-Launch Checklist

- [ ] AWS credentials configured
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] ChromeDriver available (for Selenium)
- [ ] Port 5000 available
- [ ] Email credentials set (optional, for notifications)
- [ ] S3 bucket `s3-vector-storage` exists

---

## 🚨 Troubleshooting

### API Won't Start
```powershell
# Check if port is in use
netstat -ano | findstr :5000

# Kill process if needed
taskkill /PID <pid> /F
```

### Scripts Not Showing
1. Check instance ID in `.env`
2. Verify `instance_script_assignments.json` exists
3. Check browser console (F12) for errors

### Can't Start Scripts
1. Verify script files exist in `scripts/scriptN/`
2. Check AWS credentials
3. View API logs for errors

---

## 📞 Quick Commands

```powershell
# View API logs
cat api+ui\api_server.log

# View script logs
cat scripts\script1\script1.log

# Check script status (JSON)
cat scripts\script1\script1_progress.json

# Test API health
curl http://35.226.62.197/api/health
```

---

## 🎯 Recommended Workflow

### Phase 1: Testing (Day 1)
1. Start **Instance 1** only
2. Launch **2-3 scripts**
3. Monitor for **15-30 minutes**
4. Check CPU, memory, disk usage

### Phase 2: Scaling (Day 2-3)
1. If stable, increase to **5-10 scripts** on Instance 1
2. Monitor for **1-2 hours**
3. Deploy **Instance 2** with 5-10 scripts
4. Continue monitoring

### Phase 3: Full Deployment (Day 4+)
1. All instances running
2. Gradually increase to **all scripts**
3. Monitor email notifications
4. Track overall progress

---

## 💡 Tips

- **Start small**: Begin with 2-3 scripts per instance
- **Monitor closely**: Watch CPU/memory for first hour
- **Stagger starts**: Use 5-10 second delays initially
- **Check logs**: Review logs every few hours
- **Email alerts**: Enable for error notifications
- **Backup progress**: Regularly backup `*_progress.json` files

---

## 🔗 Important URLs

- **Dashboard**: `http://35.226.62.197/`
- **API Docs**: See `README.md` for all endpoints
- **Health Check**: `http://35.226.62.197/api/health`

---

## 📚 Full Documentation

For complete details, see: **README.md**

---

**Ready to scrape 16.8M+ PDFs? Let's go! 🚀**
