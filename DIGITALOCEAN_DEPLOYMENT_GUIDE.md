# DigitalOcean Deployment Guide

Complete step-by-step guide to deploy your PropsWorks Flask application on DigitalOcean.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Option A: DigitalOcean App Platform (Recommended)](#option-a-digitalocean-app-platform-recommended)
3. [Option B: DigitalOcean Droplet (Advanced)](#option-b-digitalocean-droplet-advanced)
4. [Setting Up Custom Domain](#setting-up-custom-domain)
5. [Environment Variables](#environment-variables)
6. [Database Setup](#database-setup)
7. [Monitoring & Maintenance](#monitoring--maintenance)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before deploying, ensure you have:

- ✅ GitHub account with your repository pushed
- ✅ DigitalOcean account (sign up at digitalocean.com)
- ✅ Docker configured (already done - you have Dockerfile)
- ✅ All environment variables identified
- ✅ Database backup created locally

**Optional but recommended:**
- A custom domain (propsworks.com, etc.)
- Admin password and API keys ready

---

## Option A: DigitalOcean App Platform (Recommended)

### Why App Platform?
- ✅ Zero Docker knowledge needed
- ✅ Automatic deployment on git push
- ✅ Auto-scaling
- ✅ Free SSL certificates
- ✅ Managed PostgreSQL database
- ✅ Simple environment variable management

### Step 1: Create DigitalOcean Account

1. **Sign up** at [digitalocean.com](https://digitalocean.com)
2. **Verify email** and set up billing
3. Optional: Enter referral code for $200 credit

### Step 2: Connect GitHub Repository

1. Go to **DigitalOcean Dashboard**
2. Click **Create** → **Apps**
3. Click **GitHub** (in the source list)
4. Click **Authorize DigitalOcean** to connect GitHub
5. Select your `e3website` repository
6. Choose **main** branch for deployment
7. Click **Next**

### Step 3: Configure App Settings

#### App Name
```
propsworks-app
```

#### Resource Configuration
Digital Ocean will auto-detect your Dockerfile. Verify:
- **Source type:** GitHub repository
- **Build command:** (leave empty - uses Dockerfile)
- **Run command:** (leave empty - uses Dockerfile CMD)
- **HTTP ports:** 8080 (matches Flask)

#### Service Settings
```
Service Name: web
Resource Type: Basic (Starter)
HTTP Routes: /
```

Click **Next**

### Step 4: Add Database

1. Click **Create a new component** (PostgreSQL)
2. **Database name:** `ecommerce_db`
3. **Version:** 14 (latest stable)
4. **Engine:** PostgreSQL
5. Click **Create Component**

**Important:** Database credentials will be automatically injected as environment variables:
- `DB_HOST`
- `DB_NAME`
- `DB_PORT`
- `DB_USER`
- `DB_PASSWORD`

### Step 5: Set Environment Variables

In the **Environment** section, click **Edit** and add:

```
ADMIN_PASSWORD=your_secure_password_here
FLASK_ENV=production
FLASK_APP=wsgi.py
SQUARE_SANDBOX_KEY=your_square_sandbox_key
SQUARE_SANDBOX_TOKEN=your_square_production_token
SECRET_KEY=generate_a_secure_random_key_here
```

**To generate SECRET_KEY in Python:**
```python
python -c "import secrets; print(secrets.token_hex(32))"
```

**Square API Keys:**
- Get from: [Square Dashboard → Developer → API Keys](https://developer.squareup.com/apps)
- Use Sandbox keys for testing
- Use Production keys for live payments

### Step 6: Review & Deploy

1. Review all settings on the summary page
2. Click **Create Resources** to provision infrastructure
3. Click **Deploy App** to start deployment

**Deployment takes 5-10 minutes.** Monitor in the **Deployments** tab.

### Step 7: Access Your App

Once deployed, DigitalOcean provides:
```
App URL: https://propsworks-app-xxxxx.ondigitalocean.app
```

Visit this URL to verify your app is running!

---

## Option B: DigitalOcean Droplet (Advanced)

For more control or cost savings, use a virtual server (Droplet).

### Step 1: Create Droplet

1. **DigitalOcean Dashboard** → **Create** → **Droplets**
2. **Choose Image:** Ubuntu 22.04 (LTS)
3. **Choose Size:** Basic ($5/month) or Standard ($6/month)
4. **Choose Region:** Closest to your users
5. **Add SSH Key** (recommended over password)
6. **Hostname:** `propsworks`
7. **Create Droplet**

### Step 2: SSH into Droplet

```bash
ssh root@your_droplet_ip
```

### Step 3: Install Dependencies

```bash
# Update system
apt update && apt upgrade -y

# Install Python, pip, git
apt install -y python3 python3-pip python3-venv git

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install PostgreSQL client
apt install -y postgresql-client
```

### Step 4: Clone Repository

```bash
cd /opt
git clone https://github.com/eric4oo/e3website.git
cd e3website
```

### Step 5: Set Up Environment

```bash
# Create .env file
nano .env
```

Add:
```
FLASK_ENV=production
FLASK_APP=wsgi.py
ADMIN_PASSWORD=your_password
SQUARE_SANDBOX_KEY=your_key
SQUARE_SANDBOX_TOKEN=your_token
SECRET_KEY=your_secret_key
DATABASE_URL=postgresql://user:password@db_host:5432/ecommerce_db
```

### Step 6: Create Database (PostgreSQL)

Option A - Use DigitalOcean managed database:
1. Create PostgreSQL cluster in DigitalOcean
2. Copy connection string to `.env`

Option B - Install PostgreSQL on Droplet:
```bash
apt install -y postgresql postgresql-contrib

# Start service
systemctl start postgresql
systemctl enable postgresql

# Create database
sudo -u postgres createdb ecommerce_db
sudo -u postgres createuser appuser
sudo -u postgres psql -c "ALTER USER appuser PASSWORD 'your_password';"
```

### Step 7: Set Up Python Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 8: Initialize Database

```bash
# Inside venv
python -c "from app import create_app, db; app = create_app('production'); app.app_context().push(); db.create_all()"
```

### Step 9: Set Up Gunicorn & Nginx

**Create Gunicorn service:**
```bash
# Create systemd service file
nano /etc/systemd/system/propsworks.service
```

Add:
```ini
[Unit]
Description=PropsWorks WSGI Application
After=network.target

[Service]
User=root
WorkingDirectory=/opt/e3website
Environment="PATH=/opt/e3website/venv/bin"
ExecStart=/opt/e3website/venv/bin/gunicorn -w 4 -b 127.0.0.1:8000 wsgi:app

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
systemctl daemon-reload
systemctl enable propsworks
systemctl start propsworks
```

**Set up Nginx reverse proxy:**
```bash
apt install -y nginx
```

Create config:
```bash
nano /etc/nginx/sites-available/propsworks
```

Add:
```nginx
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /opt/e3website/static/;
    }
}
```

Enable site:
```bash
ln -s /etc/nginx/sites-available/propsworks /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

### Step 10: Set Up SSL with Let's Encrypt

```bash
apt install -y certbot python3-certbot-nginx
certbot --nginx -d yourdomain.com
```

---

## Setting Up Custom Domain

### Using DigitalOcean App Platform

1. **Go to App Settings** → **Domains**
2. **Click "Add Domain"**
3. **Enter domain:** `propsworks.com`
4. **Choose DNS option:**

#### Option A: Use DigitalOcean's Nameservers (Easiest)

1. Copy nameservers shown:
   - `ns1.digitalocean.com`
   - `ns2.digitalocean.com`
   - `ns3.digitalocean.com`

2. **Go to your domain registrar** (Namecheap, GoDaddy, etc.)

3. **Update nameservers** to DigitalOcean's

4. **Wait 24-48 hours** for propagation

#### Option B: Use CNAME Record (If keeping registrar)

1. **In DigitalOcean**, copy the **CNAME target** shown
2. **Go to your registrar's DNS settings**
3. **Add CNAME record:**
   - **Host:** `www`
   - **Points to:** `your-app.ondigitalocean.app`
4. **Optional - Add A record for root domain**
   - Create an `@` A record pointing to DigitalOcean's IP

### Using Droplet with DNS

1. **Get your Droplet's IP address**
2. **Go to registrar's DNS settings**
3. **Add A record:**
   - **Host:** `@` (root) or `www`
   - **Value:** Your Droplet's IP
4. **Wait for propagation**

### Verify DNS

```bash
nslookup propsworks.com
# Should resolve to DigitalOcean's IP
```

Or use: [whatsmydns.net](https://whatsmydns.net)

---

## Environment Variables

### Required Variables

```env
# Flask
FLASK_ENV=production
FLASK_APP=wsgi.py
SECRET_KEY=generate_secure_key_with_secrets.token_hex(32)

# Admin
ADMIN_PASSWORD=your_secure_admin_password

# Square Payment (for e-commerce)
SQUARE_SANDBOX_KEY=sq_test_xxxxxxxxxxxxxxxx
SQUARE_SANDBOX_TOKEN=sq_test_xxxxxxxxxxxxxxxx

# Database (auto-provided by DigitalOcean if using managed DB)
DB_HOST=db-host.ondigitalocean.com
DB_NAME=ecommerce_db
DB_USER=appuser
DB_PASSWORD=your_db_password
DB_PORT=5432
```

### Optional Variables

```env
# Email notifications
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password

# Analytics
GOOGLE_ANALYTICS_ID=UA-XXXXXXXXX-X

# Instagram
INSTAGRAM_HANDLE=your_handle
```

---

## Database Setup

### Using DigitalOcean Managed PostgreSQL

**Recommended for production - automatic backups, no maintenance**

1. **Create cluster** in DigitalOcean
2. **Copy connection string** from cluster details
3. **Add to environment variables**
4. **Update `config.py`:**

```python
import os
from urllib.parse import urlparse

DATABASE_URL = os.getenv('DATABASE_URL')
db_config = urlparse(DATABASE_URL)

class ProductionConfig:
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
```

### Migrating Data from SQLite to PostgreSQL

```bash
# Export SQLite data
sqlite3 instance/ecommerce.db ".dump" > backup.sql

# Import to PostgreSQL
psql -d ecommerce_db < backup.sql
```

Or use Python:
```python
from app import create_app, db
from app.models import *

app = create_app('production')

with app.app_context():
    # Create all tables
    db.create_all()
    
    # If you have existing data, import it here
    # This depends on your data structure
```

---

## Monitoring & Maintenance

### Monitor Your App

**DigitalOcean App Platform:**
- **Dashboard** → Your App → **Metrics**
  - CPU usage
  - Memory usage
  - Request count
  - Response times

**Set up alerts:**
- High CPU usage
- High memory usage
- App crashes

### View Logs

**App Platform:**
```
Dashboard → Your App → Logs
```

**Droplet (via SSH):**
```bash
# Gunicorn logs
journalctl -u propsworks -f

# Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# System logs
journalctl -f
```

### Backup Database

**Managed PostgreSQL:**
- DigitalOcean automatic backups (enabled by default)
- 7-day retention
- Manual backups anytime in cluster settings

**Export backup:**
```bash
pg_dump -U appuser -h db-host ecommerce_db > backup.sql
```

### Update Your App

```bash
# SSH into Droplet
ssh root@your_droplet_ip

# Pull latest code
cd /opt/e3website
git pull origin main

# Restart service
systemctl restart propsworks
```

**App Platform:** Auto-deploys on git push to main branch

### Scale Your App

**App Platform:**
- Go to **Settings** → service
- Adjust **instance count** or **resource size**
- Changes deploy automatically

---

## Troubleshooting

### App Won't Start

**Check logs:**
```bash
# App Platform
Dashboard → Logs tab

# Droplet
journalctl -u propsworks -n 50
```

**Common issues:**
- Environment variables not set
- Database connection string wrong
- Port already in use
- Missing dependencies

### Database Connection Error

```
Error: could not connect to server: No such file or directory
```

**Solution:**
- Verify `DATABASE_URL` environment variable
- Check database cluster is running
- Verify firewall allows connection
- Test connection:
  ```bash
  psql postgresql://user:password@host:5432/dbname
  ```

### 502 Bad Gateway Error

**Droplet:**
```bash
# Check Nginx
nginx -t

# Check Gunicorn
systemctl status propsworks

# Restart services
systemctl restart gunicorn
systemctl restart nginx
```

**App Platform:**
- Check if app crashed (Metrics tab)
- Review Logs
- Redeploy: Go to Deployments → Retry

### Payment Processing Not Working

1. **Verify Square API keys:**
   - Correct environment variables
   - Using correct keys (Sandbox vs Production)
   - Keys have proper permissions

2. **Test in Sandbox:**
   - Use test card: 4111 1111 1111 1111
   - Any future expiration date
   - Any 3-digit CVV

3. **Enable logging:**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### High Memory Usage

This usually means:
- Too many running processes
- Memory leak in app
- Large media files being cached

**Solutions:**
1. Increase instance size
2. Enable caching headers
3. Optimize database queries
4. Add CDN for static files (DigitalOcean Spaces)

---

## Best Practices

✅ **Do:**
- Keep main branch deployable
- Test locally before pushing
- Use environment variables for secrets
- Enable backups
- Monitor app regularly
- Update dependencies regularly
- Use HTTPS only
- Keep database indexed

❌ **Don't:**
- Commit API keys or passwords
- Use SQLite in production
- Ignore error logs
- Store large files in database
- Deploy untested code
- Skip SSL/HTTPS
- Forget to backup data

---

## Final Checklist

Before going live:

- [ ] GitHub repository connected
- [ ] All environment variables set
- [ ] Database created and initialized
- [ ] Admin password configured
- [ ] Square API keys working
- [ ] Domain purchased and connected
- [ ] SSL certificate installed
- [ ] Email notifications tested
- [ ] Payment processing tested
- [ ] Backup strategy implemented
- [ ] Monitoring set up
- [ ] Analytics configured

---

## Support & Resources

- **DigitalOcean Docs:** https://docs.digitalocean.com
- **Flask Deployment:** https://flask.palletsprojects.com/deploying/
- **PostgreSQL Docs:** https://www.postgresql.org/docs/
- **Nginx Guide:** https://nginx.org/en/docs/

---

## Quick Reference

### Access Your App
```
App Platform: https://propsworks-app-xxxxx.ondigitalocean.app
Custom Domain: https://propsworks.com
```

### SSH into Droplet
```bash
ssh root@your_droplet_ip
```

### View Logs
```bash
# App Platform: Dashboard → Logs
# Droplet:
journalctl -u propsworks -f
```

### Redeploy App
```bash
# App Platform: Automatic on git push
# Droplet:
cd /opt/e3website
git pull
systemctl restart propsworks
```

---

**Last Updated:** February 18, 2026

For questions or issues, check the troubleshooting section or contact DigitalOcean support.
