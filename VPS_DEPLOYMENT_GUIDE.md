# 🌐 SENTINEL HUB - LOCAL & VPS DEPLOYMENT GUIDE

**Status**: ✅ **COMPATIBLE WITH BOTH LOCAL & VPS**  
**Last Updated**: 2026-06-23

---

## ✅ YES - RUNS ON BOTH LOCAL AND VPS

```
LOCAL (Your Machine)
├─ streamlit run dashboard.py
├─ Port: 8501 (localhost only)
└─ Access: http://localhost:8501 ✅

VPS (Remote Server)
├─ streamlit run dashboard.py --server.address 0.0.0.0
├─ Port: 8501 (network accessible)
└─ Access: http://VPS_IP:8501 ✅
```

---

## 🏠 LOCAL DEPLOYMENT (Current Setup)

### Quick Start
```bash
# Already configured and working
python run_dashboard.py

# Open in browser
http://localhost:8501
```

### Files Required
- `dashboard.py`
- `run_dashboard.py`
- `.env` (with credentials)
- `src/` (bot code)
- `logs/` (directory)

---

## 🖥️ VPS DEPLOYMENT (Linux/Ubuntu)

### Prerequisites
```bash
# SSH into VPS
ssh user@your_vps_ip

# Install Python 3.9+
python3 --version

# Install pip
pip3 install --upgrade pip

# Install dependencies
pip3 install streamlit pandas psutil python-dotenv rich
```

### Step 1: Copy Files to VPS
```bash
# From your local machine
scp -r . user@your_vps_ip:/home/user/antigravity

# Verify copy
ssh user@your_vps_ip "ls /home/user/antigravity/"
```

### Step 2: Create .env File on VPS
```bash
# SSH into VPS
ssh user@your_vps_ip

# Navigate to project
cd /home/user/antigravity

# Create .env with your credentials
cat > .env << 'ENVFILE'
API_KEY=your_api_key_here
API_SECRET=your_api_secret_here
CLIENT_CODE=your_client_code_here
PASSWORD=your_password_here
ENVFILE

# Secure the file
chmod 0o600 .env
```

### Step 3: Run Dashboard on VPS

#### Option A: Direct Terminal
```bash
# Simple - blocks terminal
streamlit run dashboard.py --server.address 0.0.0.0 --server.port 8501

# Accessible at: http://your_vps_ip:8501
```

#### Option B: Background Process (Recommended)
```bash
# Run in background with nohup
nohup streamlit run dashboard.py --server.address 0.0.0.0 --server.port 8501 > logs/dashboard.log 2>&1 &

# Check if running
ps aux | grep streamlit

# View logs
tail -f logs/dashboard.log

# Stop dashboard
pkill -f "streamlit run"
```

#### Option C: Systemd Service (Best Practice)
```bash
# Create service file
sudo tee /etc/systemd/system/sentinel-hub.service << 'SERVICE'
[Unit]
Description=SENTINEL HUB Dashboard
After=network.target

[Service]
Type=simple
User=user
WorkingDirectory=/home/user/antigravity
ExecStart=/usr/bin/python3 -m streamlit run dashboard.py --server.address 0.0.0.0 --server.port 8501
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICE

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable sentinel-hub
sudo systemctl start sentinel-hub

# Check status
sudo systemctl status sentinel-hub

# View logs
sudo journalctl -u sentinel-hub -f
```

#### Option D: Docker Container (Most Portable)
```bash
# Create Dockerfile
cat > Dockerfile << 'DOCKER'
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run dashboard accessible from outside container
CMD ["streamlit", "run", "dashboard.py", "--server.address", "0.0.0.0", "--server.port", "8501"]
DOCKER

# Build image
docker build -t sentinel-hub:latest .

# Run container
docker run -d \
  --name sentinel-hub \
  -p 8501:8501 \
  --env-file .env \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/data:/app/data \
  sentinel-hub:latest

# Access at: http://your_vps_ip:8501
```

---

## 🔐 SECURITY CONSIDERATIONS

### For Both Local & VPS

✅ **Already Implemented:**
- `.env` file for credentials (not in git)
- File permissions: `chmod 0o600` on `.env`
- Credential encryption in dashboard
- Audit logging without plaintext secrets

⚠️ **VPS-Specific Recommendations:**

1. **Firewall Configuration**
```bash
# Only allow your IP
sudo ufw allow from YOUR_IP to any port 8501

# Or use SSH tunnel instead (more secure)
ssh -L 8501:localhost:8501 user@your_vps_ip
# Then access: http://localhost:8501
```

2. **SSL/HTTPS (if exposing to internet)**
```bash
# Use reverse proxy (nginx/Apache)
# or Streamlit's built-in: --logger.level=error

# Recommended: Cloudflare Tunnel (no firewall needed)
# or SSH tunnel for private access
```

3. **Environment Variables on VPS**
```bash
# Don't commit .env to git
echo ".env" >> .gitignore

# Set permissions
chmod 0o600 .env

# On VPS, use:
export API_KEY="your_key"
export API_SECRET="your_secret"
# or pass via systemd EnvironmentFile=
```

---

## 📊 COMPARISON: LOCAL vs VPS

| Feature | Local | VPS |
|---------|-------|-----|
| **Setup Time** | 2 min | 10 min |
| **Cost** | Free | $5-50/month |
| **Always On** | ❌ (if you turn off machine) | ✅ 24/7 |
| **Accessible from anywhere** | ❌ | ✅ |
| **Resource constraints** | None (unlimited) | Limited (RAM/CPU) |
| **Configuration** | Simple | Requires systemd/Docker |
| **Maintenance** | Minimal | Auto-restart needed |

---

## 🎯 RECOMMENDED SETUP

### For Development
```
Local Machine + Streamlit
├─ Fast iteration
├─ Easy debugging
└─ No deployment complexity
```

### For Production/Monitoring
```
VPS + Systemd Service + Auto-restart
├─ 24/7 uptime
├─ Survives reboots
├─ Remote access
└─ Easy log monitoring
```

### For Maximum Security
```
VPS + SSH Tunnel + No public port
├─ Firewall protected
├─ Encrypted connection
└─ Zero exposure
```

---

## 🚀 QUICK VPS DEPLOYMENT (5 STEPS)

```bash
# 1. SSH into VPS
ssh user@your_vps_ip

# 2. Clone/copy project
cd /home/user && git clone <your-repo>
cd antigravity

# 3. Install dependencies
pip3 install -r requirements.txt

# 4. Create .env with credentials
cat > .env << 'EOF'
API_KEY=your_key
API_SECRET=your_secret
CLIENT_CODE=your_code
PASSWORD=your_pass
EOF
chmod 0o600 .env

# 5. Run with systemd
sudo tee /etc/systemd/system/sentinel-hub.service > /dev/null << 'EOF'
[Unit]
Description=SENTINEL HUB
After=network.target

[Service]
Type=simple
User=user
WorkingDirectory=/home/user/antigravity
ExecStart=/usr/bin/python3 -m streamlit run dashboard.py --server.address 0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable sentinel-hub
sudo systemctl start sentinel-hub

# Access at: http://your_vps_ip:8501
```

---

## 🔧 TROUBLESHOOTING VPS

### Port Already in Use
```bash
# Check what's using port 8501
sudo lsof -i :8501

# Change port if needed
streamlit run dashboard.py --server.port 8502
```

### Can't Access Dashboard from Browser
```bash
# Check if service is running
ps aux | grep streamlit

# Check firewall
sudo ufw status
sudo ufw allow 8501

# Check if listening on all interfaces
sudo ss -tlnp | grep 8501
```

### Credentials Not Loading
```bash
# Verify .env exists
cat /home/user/antigravity/.env

# Check permissions
ls -la /home/user/antigravity/.env
# Should show: -rw------- (600)

# Test env loading
python3 -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('API_KEY'))"
```

---

## ✅ FINAL CHECKLIST

### Before Deployment
- [ ] Python 3.9+ installed
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] `.env` file created with credentials
- [ ] `.env` permissions set: `chmod 0o600 .env`
- [ ] Git: `.env` added to `.gitignore`

### Local Machine
- [ ] Dashboard runs: `python run_dashboard.py`
- [ ] Accessible at: `http://localhost:8501`
- [ ] All features working (settings, toggle, kill switch)

### VPS Machine
- [ ] SSH access verified
- [ ] Files copied to VPS
- [ ] `.env` secured on VPS
- [ ] Service running: `sudo systemctl status sentinel-hub`
- [ ] Dashboard accessible: `http://VPS_IP:8501`
- [ ] Firewall configured appropriately

---

## 🎉 READY FOR BOTH!

SENTINEL HUB is **production-ready** for:
- ✅ Local development machines
- ✅ Remote VPS servers
- ✅ Docker containers
- ✅ Cloud platforms (AWS/Azure/GCP)

Choose your deployment method based on your needs:
- **Development**: Local + `python run_dashboard.py`
- **Monitoring**: VPS + Systemd service
- **Distributed**: Docker + Kubernetes

---

**Status**: Ready to enhance with API settings, mode toggle, and kill switch! 🚀
