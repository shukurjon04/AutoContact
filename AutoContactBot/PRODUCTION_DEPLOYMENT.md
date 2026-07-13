# 🚀 PRODUCTION DEPLOYMENT GUIDE

## 🖥️ **SERVER REQUIREMENTS**

### Minimum Spec
```
- CPU:       2+ cores
- RAM:       4GB minimum (8GB recommended)
- Storage:   50GB SSD
- Network:   50 Mbps+ (1 Gbps recommended)
- OS:        Ubuntu 22.04 LTS or newer
```

### Recommended Spec
```
- CPU:       4+ cores
- RAM:       8-16GB
- Storage:   100GB+ SSD
- Network:   1 Gbps
- OS:        Ubuntu 22.04 LTS
```

---

## 🌐 **SERVER OPTIONS**

### Option 1: **VPS (Virtual Private Server)** ✅ (Recommended)

**Providers:**
| Provider | Cost | Rating | Notes |
|----------|------|--------|-------|
| **DigitalOcean** | $4-$24/month | ⭐⭐⭐⭐⭐ | Easiest, great for beginners |
| **Linode** | $5-$30/month | ⭐⭐⭐⭐⭐ | Excellent performance |
| **Vultr** | $2.50-$24/month | ⭐⭐⭐⭐ | Very cheap, good support |
| **Hetzner** | €3-€20/month | ⭐⭐⭐⭐⭐ | Europe-based, excellent value |
| **AWS Lightsail** | $3.50-$40/month | ⭐⭐⭐⭐ | AWS ecosystem |

**Best For:** Small to medium projects, easy to manage

**Pros:**
- ✅ Affordable
- ✅ Easy to setup
- ✅ Full control
- ✅ Good performance
- ✅ Excellent support

---

### Option 2: **Cloud Platforms** (Advanced)

#### **AWS (Amazon Web Services)**
```
Services needed:
- EC2 (Compute)
- RDS (PostgreSQL)
- ElastiCache (Redis)
- S3 (File storage)
- CloudFront (CDN)

Cost: ~$50-$200+/month
Best for: Large scale, heavy traffic
```

#### **Google Cloud Platform**
```
Services needed:
- Compute Engine (VM)
- Cloud SQL (PostgreSQL)
- Memorystore (Redis)
- Cloud Storage (Files)
- Cloud CDN

Cost: ~$50-$200+/month
Best for: Google ecosystem users
```

#### **Azure (Microsoft)**
```
Services needed:
- Virtual Machines
- Database for PostgreSQL
- Azure Cache for Redis
- Blob Storage
- CDN

Cost: ~$50-$200+/month
Best for: Microsoft ecosystem
```

---

### Option 3: **Shared Hosting** (NOT Recommended)

❌ **Pros:** Cheap
❌ **Cons:**
- No Docker support
- Limited customization
- Shared resources
- Poor performance for this app

---

## ✅ **RECOMMENDED: DigitalOcean Droplet**

### Why DigitalOcean?
- ✅ $4/month starting price
- ✅ Docker pre-installed option
- ✅ Simple interface
- ✅ Excellent documentation
- ✅ Great community
- ✅ One-click deployments

### Step 1: Create Droplet

1. Go to: https://digitalocean.com
2. Click "Create" → "Droplets"
3. Select:
   - **Image:** Ubuntu 22.04 LTS
   - **Plan:** Basic ($6-$24/month)
   - **Region:** Nearest to users
   - **Authentication:** SSH key
4. Click "Create Droplet"
5. Note the IP address

### Step 2: SSH Access

```bash
# macOS/Linux
ssh root@YOUR_IP

# Windows (PowerShell)
ssh root@YOUR_IP
```

---

## 📋 **COMPLETE DEPLOYMENT STEPS**

### Step 1: Server Setup

```bash
# SSH to server
ssh root@YOUR_SERVER_IP

# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Verify installation
docker --version
docker-compose --version
```

### Step 2: Domain Setup

```bash
# Point domain to server IP in DNS
# Example DNS records:
# A    yourdomain.com      -> YOUR_SERVER_IP
# A    www.yourdomain.com  -> YOUR_SERVER_IP
# A    api.yourdomain.com  -> YOUR_SERVER_IP (optional)

# Wait 24 hours for DNS propagation
# Test: ping yourdomain.com
```

### Step 3: Project Setup

```bash
# Create app directory
mkdir -p /app/subbot
cd /app/subbot

# Clone backend
git clone <backend-repo> .

# Clone frontend
git clone <frontend-repo> ../subbot-frontend

# Setup environment
cp .env.example .env
nano .env

# Update .env with:
# DEBUG=False
# SECRET_KEY=very-long-random-key
# DOMAIN=yourdomain.com
# DB_PASSWORD=strong-password
# etc.
```

### Step 4: SSL Certificate

```bash
# Create Let's Encrypt certificate
apt install certbot -y

# Generate certificate
certbot certonly --standalone \
  -d yourdomain.com \
  -d www.yourdomain.com \
  -e admin@yourdomain.com \
  --agree-tos

# Certificates stored in:
# /etc/letsencrypt/live/yourdomain.com/
```

### Step 5: Start Services

```bash
cd /app/subbot

# Build images
docker compose build

# Start all services
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f
```

### Step 6: Database Setup

```bash
# Run migrations
docker compose exec django python manage.py migrate

# Create superuser
docker compose exec django python manage.py createsuperuser

# Collect static files
docker compose exec django python manage.py collectstatic --noinput
```

### Step 7: Verify Deployment

```bash
# Test health check
curl https://yourdomain.com/health/

# Test API
curl https://yourdomain.com/api/v1/users/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# Open in browser
# https://yourdomain.com
```

---

## 🔐 **SSL/TLS WITH CERTBOT**

### Automatic Renewal

```bash
# Create renewal script
cat > /usr/local/bin/renew-cert.sh << 'EOF'
#!/bin/bash
certbot renew --quiet
docker compose -f /app/subbot/docker-compose.yml restart frontend
EOF

chmod +x /usr/local/bin/renew-cert.sh

# Add to crontab (auto-renewal every 2 months)
crontab -e

# Add line:
# 0 0 1 */2 * /usr/local/bin/renew-cert.sh
```

---

## 📊 **.env PRODUCTION TEMPLATE**

```bash
# ==============================================================================
# DOMAIN & SSL
# ==============================================================================
DOMAIN=yourdomain.com
CERTBOT_EMAIL=admin@yourdomain.com

# ==============================================================================
# DJANGO
# ==============================================================================
DEBUG=False
SECRET_KEY=generate-with-django-secret-key-generator-min-50-chars
DJANGO_SETTINGS_MODULE=config.settings.production
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
CORS_ALLOWED_ORIGINS=https://yourdomain.com

# ==============================================================================
# DATABASE
# ==============================================================================
DB_NAME=subscription_bot_db
DB_USER=subscription_bot_user
DB_PASSWORD=generate-strong-password-min-32-chars
DB_HOST=postgres
DB_PORT=5432

# ==============================================================================
# REDIS
# ==============================================================================
REDIS_PASSWORD=generate-strong-password-min-32-chars
REDIS_URL=redis://:password@redis:6379/0

# ==============================================================================
# TELEGRAM BOT
# ==============================================================================
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
TELEGRAM_ADMIN_IDS=123456789,987654321
WEBHOOK_HOST=https://yourdomain.com
WEBHOOK_PATH=/bot/webhook
WEBHOOK_SECRET_TOKEN=generate-random-secret-token

# ==============================================================================
# PAYME INTEGRATION (if using)
# ==============================================================================
PAYME_MERCHANT_ID=your_merchant_id
PAYME_SECRET_KEY=your_secret_key
PAYME_TEST_MODE=False
```

---

## 🔄 **MAINTENANCE**

### Daily Tasks
```bash
# Check status
docker compose ps

# View logs
docker compose logs -f --tail=100
```

### Weekly Tasks
```bash
# Backup database
docker compose exec postgres pg_dump -U subscription_bot_user \
  subscription_bot_db > backup-$(date +%Y%m%d).sql

# Check disk usage
df -h

# Check memory usage
free -h
```

### Monthly Tasks
```bash
# Update packages
apt update && apt upgrade -y

# Update Docker images
docker compose pull
docker compose up -d

# Check certificate expiry
certbot certificates

# Clean up
docker system prune -a --volumes
```

---

## 📦 **BACKUP & RESTORE**

### Database Backup

```bash
# Backup
docker compose exec postgres pg_dump -U subscription_bot_user \
  subscription_bot_db > backup.sql

# Backup to compressed file
docker compose exec -T postgres pg_dump -U subscription_bot_user \
  subscription_bot_db | gzip > backup-$(date +%Y%m%d).sql.gz

# Restore from file
docker compose exec -T postgres psql -U subscription_bot_user \
  subscription_bot_db < backup.sql
```

### Automated Daily Backup

```bash
# Create backup script
cat > /usr/local/bin/daily-backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backups/subbot"
mkdir -p $BACKUP_DIR
cd /app/subbot

# Backup database
docker compose exec -T postgres pg_dump -U subscription_bot_user \
  subscription_bot_db | gzip > $BACKUP_DIR/db-$(date +%Y%m%d-%H%M%S).sql.gz

# Keep only last 30 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete

# Backup uploads
tar czf $BACKUP_DIR/media-$(date +%Y%m%d-%H%M%S).tar.gz media/

# Keep only last 7 days
find $BACKUP_DIR -name "media-*.tar.gz" -mtime +7 -delete
EOF

chmod +x /usr/local/bin/daily-backup.sh

# Add to crontab
crontab -e
# Add: 0 2 * * * /usr/local/bin/daily-backup.sh
```

---

## 🔍 **MONITORING & LOGS**

### Real-time Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f django
docker compose logs -f frontend
docker compose logs -f celery_worker

# Last 100 lines
docker compose logs --tail=100
```

### Log Rotation

```bash
# Create logrotate config
cat > /etc/logrotate.d/subbot << 'EOF'
/app/subbot/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    missingok
    postrotate
        docker compose -f /app/subbot/docker-compose.yml restart django
    endscript
}
EOF
```

---

## 📈 **SCALING**

### Add More Workers

```bash
# Increase Celery workers
docker compose up -d --scale celery_worker=3
```

### Load Balancer (Advanced)

```bash
# Use Nginx for load balancing multiple instances
# or use cloud load balancer (AWS ELB, DigitalOcean LB, etc.)
```

---

## 🆘 **TROUBLESHOOTING**

### Port Already In Use
```bash
# Find process using port
lsof -i :80
lsof -i :443
lsof -i :5432

# Kill process
kill -9 <PID>
```

### Docker Disk Space
```bash
# Clean up
docker system prune -a --volumes

# Check size
docker ps -s
```

### Database Issues
```bash
# Backup and recreate
docker-compose down
docker volume rm subbot_postgres_data
docker compose up -d postgres
docker compose exec django python manage.py migrate
```

---

## 🌐 **ACCESSING SERVICES**

| Service | URL | Port | Notes |
|---------|-----|------|-------|
| **Frontend** | https://yourdomain.com | 443 | Angular SPA |
| **API** | https://yourdomain.com/api/v1/ | 443 | REST API |
| **Health** | https://yourdomain.com/health/ | 443 | Health check |
| **Database** | localhost:5432 | 5432 | Internal only |
| **Redis** | localhost:6379 | 6379 | Internal only |

---

## 💰 **COST BREAKDOWN**

### Minimal Setup
```
DigitalOcean Droplet:      $6/month
Domain:                    $10-15/year
SSL Certificate:           FREE (Let's Encrypt)
Total:                     ~$6/month
```

### Recommended Setup
```
DigitalOcean Droplet:      $12/month
PostgreSQL Backup:         $2/month
Domain:                    $10-15/year
SSL Certificate:           FREE (Let's Encrypt)
CDN (optional):            $0 free tier or $10-20/month
Total:                     ~$14/month
```

### Large Scale
```
2x Droplets (load balanced):  $24/month
PostgreSQL Managed:           $15/month
Redis Managed:               $5/month
Domain:                      $10-15/year
CDN:                         $20/month
SSL:                         FREE (Let's Encrypt)
Total:                       ~$74/month
```

---

## 🚀 **QUICK START CHECKLIST**

- [ ] Buy domain (yourdomain.com)
- [ ] Create VPS server (DigitalOcean, Linode, etc.)
- [ ] SSH to server
- [ ] Install Docker & Docker Compose
- [ ] Setup DNS records
- [ ] Generate SSL certificate
- [ ] Clone repositories
- [ ] Setup .env file
- [ ] Build Docker images
- [ ] Start all services
- [ ] Create database and superuser
- [ ] Test in browser
- [ ] Setup monitoring & backups
- [ ] Configure email alerts

---

**DEPLOYED! 🎉 Your app is now live on production!**
