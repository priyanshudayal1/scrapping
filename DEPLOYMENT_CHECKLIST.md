# 🚀 Deployment Checklist - Multi-Script Scraping System

Use this checklist to ensure proper deployment of your distributed scraping system.

---

## ✅ Pre-Deployment Setup

### Local Environment
- [ ] Python 3.8+ installed
- [ ] Git installed (for version control)
- [ ] Text editor ready (VS Code, etc.)
- [ ] Terminal/PowerShell access

### AWS Configuration
- [ ] AWS account created
- [ ] Access key ID obtained
- [ ] Secret access key obtained
- [ ] S3 bucket `s3-vector-storage` created
- [ ] S3 bucket permissions configured
- [ ] Bedrock API access enabled (for captcha solving)

### Email Setup
- [ ] Gmail account ready
- [ ] 2-factor authentication enabled
- [ ] App password generated
- [ ] SMTP access confirmed (smtp.gmail.com:587)

### VPS Instances
- [ ] 4 VPS instances provisioned
- [ ] Ubuntu/Debian Linux installed
- [ ] SSH access configured
- [ ] IP addresses documented
- [ ] Root/sudo access available

---

## 📦 Installation Steps

### 1. Local Setup
```powershell
# Clone/navigate to project directory
cd "C:\Users\Priyanshu Dayal\Desktop\judgements\Judgements Scrapping"

# Navigate to scrapping-app
cd scrapping-app

# Install dependencies
pip install -r requirements.txt
```
- [ ] Dependencies installed successfully
- [ ] No error messages

### 2. Configuration Files

#### Edit .env.instance1
```bash
INSTANCE_ID=1
AWS_ACCESS_KEY_ID=your_actual_key_here
AWS_SECRET_ACCESS_KEY=your_actual_secret_here
AWS_REGION=ap-south-1
EMAIL_HOST_USER=astutelexservicado@gmail.com
EMAIL_HOST_PASSWORD=your_app_password_here
S3_BUCKET_NAME=s3-vector-storage
```
- [ ] AWS credentials updated
- [ ] Email credentials updated
- [ ] No syntax errors

#### Repeat for .env.instance2, .env.instance3, .env.instance4
- [ ] .env.instance2 configured (INSTANCE_ID=2)
- [ ] .env.instance3 configured (INSTANCE_ID=3)
- [ ] .env.instance4 configured (INSTANCE_ID=4)

### 3. Local Testing
```powershell
# Test with Instance 1
.\start_instance1.ps1
```
- [ ] API server starts without errors
- [ ] Port 5000 is accessible
- [ ] Dashboard loads at http://localhost:5000/
- [ ] API health check responds: http://localhost:5000/api/health
- [ ] Instance info shows correct scripts: http://localhost:5000/api/instance/info

### 4. Single Script Test
In dashboard:
- [ ] Start 1 script (Script 1)
- [ ] Monitor for 5-10 minutes
- [ ] Check progress updates
- [ ] Verify S3 uploads
- [ ] Confirm local file deletion
- [ ] Review logs for errors
- [ ] Stop script successfully

### 5. Multi-Script Test
In dashboard:
- [ ] Start 3 scripts (num_scripts=3, delay=2)
- [ ] Monitor for 15-30 minutes
- [ ] Check CPU usage (should be < 80%)
- [ ] Check memory usage (should be < 75%)
- [ ] Verify all scripts running
- [ ] Confirm progress tracking
- [ ] Test "Stop All" button
- [ ] All scripts stop gracefully

---

## 🌐 VPS Deployment

### VPS 1 Setup

#### A. Transfer Files
```bash
# From local machine
scp -r scrapping-app/ user@vps1-ip:/home/user/

# OR use SFTP/WinSCP
```
- [ ] All files transferred
- [ ] Directory structure intact
- [ ] Permissions correct (chmod +x *.ps1)

#### B. Install Dependencies
```bash
# SSH into VPS 1
ssh user@vps1-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python
sudo apt install python3 python3-pip -y

# Install Chrome/ChromeDriver (for Selenium)
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt-get install -f -y

# Install ChromeDriver
wget https://chromedriver.storage.googleapis.com/LATEST_RELEASE
CHROMEDRIVER_VERSION=$(cat LATEST_RELEASE)
wget https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
sudo mv chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver

# Navigate to project
cd scrapping-app

# Install Python dependencies
pip3 install -r requirements.txt
```
- [ ] Python installed
- [ ] Chrome installed
- [ ] ChromeDriver installed
- [ ] Dependencies installed
- [ ] No error messages

#### C. Configure Environment
```bash
# Ensure .env.instance1 is configured
cat .env.instance1

# Copy to api+ui directory (startup script does this)
```
- [ ] Environment file exists
- [ ] Credentials are correct
- [ ] Instance ID is 1

#### D. Start Instance
```bash
# Make startup script executable
chmod +x start_instance1.ps1

# Start instance (use screen/tmux to keep running)
screen -S instance1
cd scrapping-app
./start_instance1.ps1

# Detach: Ctrl+A, then D
```
- [ ] API server running
- [ ] No startup errors
- [ ] Port 5000 listening
- [ ] Screen/tmux session active

#### E. Verify Access
From local machine:
```bash
# Test API
curl http://vps1-ip:5000/api/health

# Open dashboard in browser
# http://vps1-ip:5000/
```
- [ ] API responds
- [ ] Dashboard loads
- [ ] Shows correct instance (1)
- [ ] Lists scripts 1-17

### VPS 2, 3, 4 Setup
Repeat above steps for each VPS:

**VPS 2:**
- [ ] Files transferred
- [ ] Dependencies installed
- [ ] .env.instance2 configured
- [ ] start_instance2.ps1 executed
- [ ] API accessible on port 5000
- [ ] Dashboard shows scripts 18-34

**VPS 3:**
- [ ] Files transferred
- [ ] Dependencies installed
- [ ] .env.instance3 configured
- [ ] start_instance3.ps1 executed
- [ ] API accessible on port 5000
- [ ] Dashboard shows scripts 35-51

**VPS 4:**
- [ ] Files transferred
- [ ] Dependencies installed
- [ ] .env.instance4 configured
- [ ] start_instance4.ps1 executed
- [ ] API accessible on port 5000
- [ ] Dashboard shows scripts 52-66

---

## 🧪 Production Testing

### Initial Launch (Each VPS)
- [ ] Start 2-3 scripts per instance
- [ ] Monitor for 1 hour
- [ ] Check CPU (target < 70%)
- [ ] Check Memory (target < 70%)
- [ ] Check Disk I/O
- [ ] Verify S3 uploads
- [ ] Confirm email notifications
- [ ] Review logs for errors

### Gradual Scaling
**Day 1:**
- [ ] 2-3 scripts per instance (8-12 total)
- [ ] Monitor continuously
- [ ] No critical errors

**Day 2:**
- [ ] 5-8 scripts per instance (20-32 total)
- [ ] Check resource usage
- [ ] Verify data quality

**Day 3:**
- [ ] 10-12 scripts per instance (40-48 total)
- [ ] System stable
- [ ] Performance acceptable

**Week 2:**
- [ ] All 66 scripts running
- [ ] Regular monitoring in place
- [ ] Email notifications working

---

## 🔒 Security Checklist

### Firewall Configuration
```bash
# On each VPS
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 5000/tcp  # API (or restrict to specific IPs)
sudo ufw enable
```
- [ ] Firewall enabled on all VPS
- [ ] Port 5000 accessible
- [ ] SSH port secured
- [ ] Unnecessary ports blocked

### SSH Security
```bash
# Disable password auth (use keys only)
sudo nano /etc/ssh/sshd_config
# Set: PasswordAuthentication no
sudo systemctl restart sshd
```
- [ ] SSH key authentication configured
- [ ] Password authentication disabled
- [ ] Root login disabled (optional)

### Environment Variables
- [ ] .env files NOT committed to git
- [ ] AWS credentials secured
- [ ] Email credentials secured
- [ ] Backup of credentials stored safely

### HTTPS Setup (Optional but Recommended)
```bash
# Install nginx and certbot
sudo apt install nginx certbot python3-certbot-nginx -y

# Configure reverse proxy and SSL
sudo certbot --nginx -d yourdomain.com
```
- [ ] Nginx installed (if using)
- [ ] SSL certificate obtained (if using)
- [ ] HTTPS redirects configured (if using)

---

## 📊 Monitoring Setup

### System Monitoring
```bash
# Install monitoring tools
sudo apt install htop iotop iftop -y
```
- [ ] htop installed (CPU/Memory)
- [ ] iotop installed (Disk I/O)
- [ ] iftop installed (Network)

### Application Monitoring
- [ ] Dashboard bookmarked for each instance
- [ ] API health checks scheduled
- [ ] Email notifications enabled
- [ ] Log rotation configured

### Automated Checks (Optional)
```bash
# Create cron job for health checks
crontab -e

# Add:
*/5 * * * * curl -s http://localhost:5000/api/health || mail -s "VPS1 API Down" your@email.com
```
- [ ] Cron jobs created for health checks
- [ ] Alerting configured

---

## 💾 Backup Strategy

### Progress Files
```bash
# Backup script (run daily)
#!/bin/bash
tar -czf backup-$(date +%Y%m%d).tar.gz scripts/*/script*_progress.json
```
- [ ] Backup script created
- [ ] Scheduled in cron (daily)
- [ ] Backup storage configured
- [ ] Test restore procedure

### Configuration Files
- [ ] .env files backed up securely
- [ ] startup scripts backed up
- [ ] instance_script_assignments.json backed up

---

## 📞 Support Resources

### Documentation
- [ ] README.md reviewed
- [ ] QUICKSTART.md available
- [ ] ARCHITECTURE.md understood
- [ ] SUMMARY.md read

### Contact Information
- [ ] VPS provider support documented
- [ ] AWS support contact saved
- [ ] Email service contact saved

### Emergency Procedures
- [ ] "Stop All" button tested
- [ ] Manual stop procedure documented
- [ ] Restart procedure documented
- [ ] Recovery from crash tested

---

## 🎯 Success Criteria

### Technical Metrics
- [ ] All 66 scripts can start
- [ ] API responds < 500ms
- [ ] Dashboard updates every 5 seconds
- [ ] S3 uploads succeed >98%
- [ ] Email notifications delivered
- [ ] Logs properly formatted

### Performance Metrics
- [ ] CPU usage < 80% average
- [ ] Memory usage < 75%
- [ ] Disk I/O acceptable
- [ ] Network stable
- [ ] Download rate >15K PDFs/day per instance

### Operational Metrics
- [ ] Scripts restart after failure
- [ ] Progress properly saved
- [ ] No data loss
- [ ] Monitoring alerts working
- [ ] Team can access dashboards

---

## 🚀 Go-Live Checklist

### Final Verification (Before Full Launch)
- [ ] All VPS instances accessible
- [ ] All APIs responding
- [ ] All dashboards loading
- [ ] Test scripts completed successfully
- [ ] S3 uploads verified
- [ ] Email notifications received
- [ ] Logs reviewed (no critical errors)
- [ ] Backup systems tested
- [ ] Monitoring confirmed working
- [ ] Emergency procedures tested

### Launch Day
- [ ] Start 2-3 scripts per instance
- [ ] Monitor for first 2 hours continuously
- [ ] Check all dashboards
- [ ] Verify S3 uploads
- [ ] Confirm email notifications
- [ ] Review logs every 30 minutes

### First Week
- [ ] Scale to 50% capacity (33 scripts)
- [ ] Daily log reviews
- [ ] Daily backup verification
- [ ] Performance monitoring
- [ ] Address any issues immediately

### Full Production
- [ ] All 66 scripts running
- [ ] Automated monitoring in place
- [ ] Weekly progress reports
- [ ] Monthly performance reviews
- [ ] Continuous optimization

---

## 📈 KPIs to Track

### Daily
- [ ] Scripts running count
- [ ] Total PDFs downloaded
- [ ] Success rate (%)
- [ ] Error count
- [ ] S3 storage used

### Weekly
- [ ] Total progress (%)
- [ ] Average download rate
- [ ] Resource utilization
- [ ] Error trends
- [ ] Estimated completion date

### Monthly
- [ ] Overall system health
- [ ] Cost analysis (VPS + S3)
- [ ] Performance optimization opportunities
- [ ] Data quality metrics

---

## ✅ Final Sign-Off

**Deployment Completed By:** ___________________  
**Date:** ___________________  
**All Checklist Items Verified:** [ ] Yes  
**System Ready for Production:** [ ] Yes  

**Notes:**
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________

---

**🎉 Congratulations on successful deployment!**

Remember:
- Start small, scale gradually
- Monitor continuously
- Back up regularly
- Address issues promptly
- Celebrate milestones!

**Happy Scraping! 🚀**
