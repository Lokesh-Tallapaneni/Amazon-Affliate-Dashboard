# Production Deployment Guide

## Pre-Deployment Checklist

### ✅ Code Quality
- [x] PEP8 compliant
- [x] All tests passing (6/6 end-to-end, 9/9 routes)
- [x] Type hints implemented
- [x] Comprehensive logging
- [x] Error handling in place
- [x] Security best practices followed

### ✅ Configuration
- [x] Environment-based configs (dev/test/prod)
- [x] Secrets managed via environment variables
- [x] .env.example provided
- [x] Production config validated

### ✅ Dependencies
- [x] requirements.txt up to date
- [x] Virtual environment tested
- [x] All packages compatible

### ✅ Folder Structure
```
Good/
├── app/
│   ├── __init__.py           # Application factory
│   ├── logger.py             # Logging config
│   ├── blueprints/           # Route handlers
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── dashboard.py
│   │   ├── data.py
│   │   ├── recommendations.py
│   │   └── chat.py
│   ├── services/             # Business logic
│   │   ├── __init__.py
│   │   ├── amazon_api.py
│   │   ├── chat_service.py
│   │   ├── data_processor.py
│   │   ├── ml_service.py
│   │   └── product_service.py
│   └── utils/                # Utilities
│       ├── __init__.py
│       ├── decorators.py
│       ├── helpers.py
│       └── validators.py
├── static/
│   ├── images/               # Generated charts
│   ├── *.css                 # Stylesheets
├── templates/                # HTML templates
│   ├── index.html
│   ├── dash.html
│   ├── data.html
│   ├── recommendations.html
│   └── chat.html
├── logs/                     # Application logs
├── uploads/                  # User uploads (auto-created)
├── venv/                     # Virtual environment
├── config.py                 # Configuration
├── run.py                    # Entry point
├── requirements.txt          # Dependencies
├── .env                      # Environment variables (create from .env.example)
├── .env.example              # Template
└── .gitignore                # Git ignore rules
```

---

## Installation

### 1. Server Requirements

**Minimum:**
- Python 3.9+
- 2GB RAM
- 10GB disk space
- Ubuntu 20.04+ / Windows Server 2019+

**Recommended:**
- Python 3.11+
- 4GB RAM
- 20GB disk space
- Ubuntu 22.04 LTS

### 2. System Packages

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3-pip nginx supervisor
```

**CentOS/RHEL:**
```bash
sudo yum install -y python311 python311-pip nginx supervisor
```

### 3. Clone Repository

```bash
cd /var/www/
git clone <repository-url> affiliate-dashboard
cd affiliate-dashboard
```

### 4. Create Virtual Environment

```bash
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 5. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 6. Configure Environment

```bash
cp .env.example .env
nano .env  # Edit with your values
```

**Required Environment Variables:**
```env
# Flask
FLASK_ENV=production
SECRET_KEY=<generate-with-secrets-token-hex>
FLASK_HOST=0.0.0.0
FLASK_PORT=5000

# Amazon API
AMAZON_API_KEY=<your-api-key>
AMAZON_SECRET_KEY=<your-secret-key>
AMAZON_ASSOCIATE_TAG=<your-tag>

# OpenAI (for chat)
OPENAI_API_KEY=<your-openai-key>

# Logging
LOG_LEVEL=INFO
```

**Generate Secure Secret Key:**
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 7. Create Required Directories

```bash
mkdir -p logs uploads static/images
chmod 755 logs uploads static/images
```

### 8. Run Tests

```bash
# Test configuration
python test_end_to_end.py

# Should show: 🎉 ALL TESTS PASSED - PRODUCTION READY!
```

---

## Deployment Options

### Option 1: Gunicorn + Nginx (Recommended)

#### Step 1: Install Gunicorn

```bash
pip install gunicorn
```

#### Step 2: Create Gunicorn Config

Create `/var/www/affiliate-dashboard/gunicorn_config.py`:

```python
import multiprocessing

bind = "127.0.0.1:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 5

# Logging
accesslog = "/var/www/affiliate-dashboard/logs/gunicorn_access.log"
errorlog = "/var/www/affiliate-dashboard/logs/gunicorn_error.log"
loglevel = "info"

# Process naming
proc_name = "affiliate_dashboard"

# Server mechanics
daemon = False
pidfile = "/var/www/affiliate-dashboard/gunicorn.pid"
```

#### Step 3: Create Systemd Service

Create `/etc/systemd/system/affiliate-dashboard.service`:

```ini
[Unit]
Description=Amazon Affiliate Dashboard
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/affiliate-dashboard
Environment="PATH=/var/www/affiliate-dashboard/venv/bin"
EnvironmentFile=/var/www/affiliate-dashboard/.env
ExecStart=/var/www/affiliate-dashboard/venv/bin/gunicorn \
    --config /var/www/affiliate-dashboard/gunicorn_config.py \
    "app:create_app('production')"
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

#### Step 4: Configure Nginx

Create `/etc/nginx/sites-available/affiliate-dashboard`:

```nginx
upstream affiliate_dashboard {
    server 127.0.0.1:8000 fail_timeout=0;
}

server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    # SSL Configuration (use Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    client_max_body_size 16M;

    location / {
        proxy_pass http://affiliate_dashboard;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        proxy_buffering off;
    }

    location /static {
        alias /var/www/affiliate-dashboard/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Logs
    access_log /var/log/nginx/affiliate_dashboard_access.log;
    error_log /var/log/nginx/affiliate_dashboard_error.log;
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/affiliate-dashboard /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### Step 5: Start Application

```bash
# Enable and start service
sudo systemctl enable affiliate-dashboard
sudo systemctl start affiliate-dashboard

# Check status
sudo systemctl status affiliate-dashboard

# View logs
sudo journalctl -u affiliate-dashboard -f
```

---

### Option 2: Docker Deployment

#### Dockerfile

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy application
COPY . .

# Create required directories
RUN mkdir -p logs uploads static/images

# Expose port
EXPOSE 5000

# Set environment
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Run application
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "--timeout", "120", "app:create_app('production')"]
```

#### docker-compose.yml

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    env_file:
      - .env
    volumes:
      - ./logs:/app/logs
      - ./uploads:/app/uploads
      - ./static/images:/app/static/images
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/login"]
      interval: 30s
      timeout: 10s
      retries: 3
```

#### Deploy with Docker

```bash
# Build image
docker-compose build

# Start container
docker-compose up -d

# View logs
docker-compose logs -f

# Stop container
docker-compose down
```

---

## SSL/TLS Setup (Let's Encrypt)

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal (already set up by certbot)
sudo certbot renew --dry-run
```

---

## Monitoring & Maintenance

### 1. Log Rotation

Create `/etc/logrotate.d/affiliate-dashboard`:

```
/var/www/affiliate-dashboard/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    missingok
    create 0644 www-data www-data
}
```

### 2. Health Checks

Create a cron job for health monitoring:

```bash
# Check every 5 minutes
*/5 * * * * curl -f http://localhost:8000/login || systemctl restart affiliate-dashboard
```

### 3. Backups

Backup important data:

```bash
#!/bin/bash
# /usr/local/bin/backup-dashboard.sh

BACKUP_DIR="/backups/affiliate-dashboard"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup uploads and logs
tar -czf $BACKUP_DIR/data_$DATE.tar.gz \
    /var/www/affiliate-dashboard/uploads \
    /var/www/affiliate-dashboard/logs

# Keep only last 7 days
find $BACKUP_DIR -name "data_*.tar.gz" -mtime +7 -delete
```

Add to crontab:
```bash
# Daily backup at 2 AM
0 2 * * * /usr/local/bin/backup-dashboard.sh
```

### 4. Performance Monitoring

Install monitoring tools:

```bash
# Application metrics
pip install prometheus-flask-exporter

# System monitoring
sudo apt install htop netdata
```

---

## Security Hardening

### 1. Firewall (UFW)

```bash
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### 2. Fail2ban

```bash
sudo apt install fail2ban

# Configure for Nginx
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 3. Application Security

- ✅ HTTPS only
- ✅ Secure session cookies
- ✅ CSRF protection
- ✅ Input validation
- ✅ SQL injection prevention (using Pandas, no raw SQL)
- ✅ File upload restrictions
- ✅ Environment-based secrets

---

## Troubleshooting

### Service won't start

```bash
# Check logs
sudo journalctl -u affiliate-dashboard -n 50

# Check configuration
source /var/www/affiliate-dashboard/venv/bin/activate
cd /var/www/affiliate-dashboard
python run.py  # Test manually
```

### High memory usage

```bash
# Reduce Gunicorn workers
# Edit gunicorn_config.py
workers = 2  # Instead of auto-calculation
```

### Slow chart generation

```bash
# Increase timeout in gunicorn_config.py
timeout = 180
```

---

## Performance Optimization

### 1. Enable Caching

Consider Redis for:
- Session storage
- Chart caching
- ML predictions caching

### 2. Database Migration

For scalability, migrate from Excel to PostgreSQL:
- Store earnings data
- Store product data
- Faster queries

### 3. CDN Integration

Use CDN for static assets:
- Serve charts from CDN
- Cache CSS/JS files

---

## Rollback Procedure

```bash
# Stop current version
sudo systemctl stop affiliate-dashboard

# Restore previous version
cd /var/www/affiliate-dashboard
git checkout <previous-commit>

# Reinstall dependencies
source venv/bin/activate
pip install -r requirements.txt

# Restart
sudo systemctl start affiliate-dashboard
```

---

## Support & Maintenance

### Update Application

```bash
# Pull latest code
cd /var/www/affiliate-dashboard
git pull origin main

# Update dependencies
source venv/bin/activate
pip install -r requirements.txt --upgrade

# Restart service
sudo systemctl restart affiliate-dashboard
```

### Monitor Logs

```bash
# Application logs
tail -f logs/app.log

# Gunicorn logs
tail -f logs/gunicorn_error.log

# Nginx logs
tail -f /var/log/nginx/affiliate_dashboard_error.log

# System logs
sudo journalctl -u affiliate-dashboard -f
```

---

## Success Criteria

✅ Application accessible via HTTPS
✅ All routes working correctly
✅ Charts generating properly
✅ ML model training successfully
✅ Product fetching functional
✅ Logs being written
✅ No errors in logs
✅ Auto-restart on failure
✅ SSL certificate valid
✅ Backups running

---

## Post-Deployment Checklist

- [ ] Verify HTTPS works
- [ ] Test login flow
- [ ] Test file upload
- [ ] Test dashboard charts
- [ ] Test recommendations
- [ ] Test chat feature
- [ ] Verify logs are being written
- [ ] Check disk space
- [ ] Monitor CPU/RAM usage
- [ ] Set up monitoring alerts
- [ ] Configure backups
- [ ] Document any custom changes

---

**Deployment Date:** _________________
**Deployed By:** _________________
**Version:** 2.0.0 (Refactored)
**Status:** ✅ Production Ready
