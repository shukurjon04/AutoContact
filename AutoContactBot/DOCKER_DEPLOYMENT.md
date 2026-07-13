# 🐳 Docker & Deployment Guide

Complete guide for building, running, and deploying SubBot with Docker.

## Quick Start

### Development

```bash
# Clone repositories
git clone <backend-repo> AutoContactBot
cd AutoContactBot

# Create .env from template
cp .env.example .env

# Start development stack
docker compose -f docker-compose.yml -f docker-compose.dev.yml up

# Migrate database
docker compose exec django python manage.py migrate

# Create superuser
docker compose exec django python manage.py createsuperuser

# Access services
# Backend: http://localhost:8000
# Frontend: http://localhost:4200
# Django Admin: http://localhost:8000/admin/
```

### Production

```bash
# Build images
docker compose -f docker-compose.prod.yml build

# Start production stack
docker compose -f docker-compose.prod.yml up -d

# Run migrations
docker compose -f docker-compose.prod.yml exec django python manage.py migrate

# Collect static files
docker compose -f docker-compose.prod.yml exec django python manage.py collectstatic --noinput
```

## Docker Images

### Backend (Django + API)

**File:** `docker/Dockerfile.django`

Features:
- Multi-stage build for minimal size
- Python 3.11 slim image
- Gunicorn WSGI server (4 workers)
- Health checks included
- Non-root user (appuser)
- Automatic static file collection

```dockerfile
docker build -f docker/Dockerfile.django -t subbot-backend:latest .
docker run -p 8000:8000 subbot-backend:latest
```

### Frontend (Angular + Nginx)

**File:** `AutoContactBot-Frontend/Dockerfile`

Features:
- Multi-stage build (Node builder + Nginx runtime)
- Production Angular bundle
- Nginx reverse proxy
- SPA routing configured
- API proxy to backend
- Security headers
- Gzip compression
- Health checks

```dockerfile
docker build -f Dockerfile -t subbot-frontend:latest .
docker run -p 80:80 subbot-frontend:latest
```

## Services

### docker-compose.yml (Base)

Base configuration for all environments.

```yaml
services:
  - postgres     # PostgreSQL 16
  - redis        # Redis 7
  - django       # Django REST API
  - celery_worker
  - celery_beat
  - bot          # Telegram Bot
```

### docker-compose.dev.yml (Development Override)

Development-specific configuration:
- Hot reload on code changes
- Debug logging
- Exposed database port
- Development database credentials

Run with:
```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up
```

### docker-compose.prod.yml (Production)

Production-only configuration:
- Uses pre-built images
- Health checks on all services
- Restart policies
- Volumes for persistence
- SSL/TLS support ready
- Optimized resource limits

Run with:
```bash
docker compose -f docker-compose.prod.yml up -d
```

## Environment Configuration

### .env File (Development)

```bash
# Database
DB_NAME=subscription_bot_db
DB_USER=subscription_bot_user
DB_PASSWORD=dev_password

# Redis
REDIS_URL=redis://redis:6379/0

# Django
DEBUG=True
SECRET_KEY=dev-secret-key-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1,django
CORS_ALLOWED_ORIGINS=http://localhost:4200,http://127.0.0.1:4200

# Telegram
TELEGRAM_BOT_TOKEN=your_token_here
TELEGRAM_ADMIN_IDS=123456789
WEBHOOK_HOST=https://yourdomain.com
WEBHOOK_PATH=/bot/webhook
WEBHOOK_SECRET_TOKEN=your_secret

# Payme
PAYME_MERCHANT_ID=your_merchant_id
PAYME_SECRET_KEY=your_secret_key
```

### .env File (Production)

```bash
# Domain & SSL
DOMAIN=yourdomain.com
CERTBOT_EMAIL=admin@yourdomain.com

# Database
DB_NAME=subscription_bot_db
DB_USER=subscription_bot_user
DB_PASSWORD=strong_password_here_min_32_chars

# Redis
REDIS_PASSWORD=strong_redis_password_here
REDIS_URL=redis://:password@redis:6379/0

# Django
DEBUG=False
SECRET_KEY=very-secret-key-min-50-chars-change-this
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
CORS_ALLOWED_ORIGINS=https://yourdomain.com

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_production_token
TELEGRAM_ADMIN_IDS=123456789
WEBHOOK_HOST=https://yourdomain.com
WEBHOOK_SECRET_TOKEN=production_webhook_secret

# Payme
PAYME_MERCHANT_ID=production_merchant_id
PAYME_SECRET_KEY=production_secret_key
PAYME_TEST_MODE=False
```

## Networking

All services communicate via `subbot_network` bridge:

```
┌─────────────────────────────────────┐
│    subbot_network (bridge)          │
├─────────────────────────────────────┤
│  postgres → :5432                   │
│  redis    → :6379                   │
│  django   → :8000 (expose)          │
│  celery_worker                      │
│  celery_beat                        │
│  bot      → webhook listener        │
│  frontend → :80, :443               │
└─────────────────────────────────────┘
```

### Service Communication

- **Frontend → Backend**: Nginx proxy at `/api/` → `http://django:8000`
- **Django → Redis**: `redis://redis:6379/0`
- **Celery → Broker**: `redis://redis:6379/0`
- **Django → Database**: `postgres://postgres:5432`
- **Bot → Django**: TCP connection to `django:8000`

## Database Management

### Initial Setup

```bash
# Run migrations
docker compose exec django python manage.py migrate

# Create superuser
docker compose exec django python manage.py createsuperuser

# Create test data (optional)
docker compose exec django python manage.py shell < fixtures/initial_data.py
```

### Backup & Restore

```bash
# Backup database
docker compose exec postgres pg_dump -U subscription_bot_user subscription_bot_db > backup.sql

# Restore database
docker compose exec -T postgres psql -U subscription_bot_user subscription_bot_db < backup.sql

# Backup volumes
docker run --rm -v postgres_data:/data -v $(pwd):/backup \
  busybox tar czf /backup/postgres_backup.tar.gz -C /data .
```

## Logs & Monitoring

### View Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f django
docker compose logs -f celery_worker

# Production logs
docker compose -f docker-compose.prod.yml logs -f django
```

### Health Status

```bash
# Check all service health
docker compose ps

# Check specific health
docker inspect subbot_django_dev --format='{{.State.Health.Status}}'
```

### Resource Monitoring

```bash
# Monitor container stats
docker stats

# Production monitoring
docker compose -f docker-compose.prod.yml ps -a
```

## Updates & Maintenance

### Update Backend

```bash
# Development
git pull
docker compose up -d

# Production
git pull
docker compose -f docker-compose.prod.yml build django
docker compose -f docker-compose.prod.yml up -d django

# Migrations
docker compose -f docker-compose.prod.yml exec django python manage.py migrate
```

### Update Frontend

```bash
# Development
cd ../AutoContactBot-Frontend
git pull
npm install
npm run build:prod

# Production
docker compose -f docker-compose.prod.yml build frontend
docker compose -f docker-compose.prod.yml up -d frontend
```

### Update Database Schema

```bash
# Create migration
docker compose exec django python manage.py makemigrations

# Review migration
docker compose exec django cat apps/yourapp/migrations/0xxx_*.py

# Apply migration
docker compose exec django python manage.py migrate
```

## SSL/TLS Setup (Certbot)

For production with Let's Encrypt:

```bash
# Initial certificate
docker compose -f docker-compose.prod.yml run --rm certbot certonly \
  --webroot -w /var/www/certbot \
  -d yourdomain.com -d www.yourdomain.com \
  -e admin@yourdomain.com \
  --agree-tos

# Renewal (automatic with cron)
0 0 1 * * docker compose -f docker-compose.prod.yml \
  run --rm certbot renew
```

Update Nginx config after certificate setup.

## Scaling

### Multiple Workers

Edit `docker-compose.prod.yml`:

```yaml
celery_worker:
  deploy:
    replicas: 3

celery_beat:
  # Only one instance!
  deploy:
    replicas: 1
```

Scale with:
```bash
docker compose -f docker-compose.prod.yml up -d --scale celery_worker=3
```

### Database Connection Pooling

Add PgBouncer for connection pooling in production.

## Troubleshooting

### Services won't start

```bash
# Check logs
docker compose logs

# Check health
docker compose ps

# Restart all
docker compose down
docker compose up -d
```

### Database connection refused

```bash
# Ensure postgres is healthy
docker compose logs postgres

# Restart postgres
docker compose restart postgres

# Check port
docker compose port postgres 5432
```

### Redis connection refused

```bash
# Check redis health
docker compose logs redis

# Verify Redis is running
docker compose exec redis redis-cli ping

# Restart if needed
docker compose restart redis
```

### Static files not served

```bash
# Collect static files
docker compose exec django python manage.py collectstatic --noinput

# Check volume mounted
docker compose exec django ls -la /app/staticfiles

# Restart Nginx
docker compose restart frontend
```

## Security Best Practices

### .env Security
- ✅ Add `.env` to `.gitignore`
- ✅ Use strong passwords (min 32 chars)
- ✅ Rotate SECRET_KEY regularly
- ✅ Don't commit `.env` to git

### Container Security
- ✅ Use non-root users in containers
- ✅ Read-only filesystems where possible
- ✅ Network isolation with custom bridge
- ✅ Resource limits on containers

### Database Security
- ✅ Use strong PostgreSQL passwords
- ✅ Regular backups
- ✅ Encrypted volume storage
- ✅ No direct DB access from outside

### API Security
- ✅ HTTPS/SSL in production
- ✅ CORS configured for specific origins
- ✅ Rate limiting enabled
- ✅ JWT token rotation

## Performance Optimization

### Caching
- Redis for session/cache
- Browser cache for static assets (1 year)
- HTTP cache headers configured

### Database
- Connection pooling with PgBouncer (optional)
- Indexed frequently queried fields
- Query optimization

### Frontend
- Production bundle (minified, tree-shaken)
- Gzip compression (nginx)
- Asset versioning for cache busting

### Celery
- Worker concurrency tuned (4 workers default)
- Task retry logic
- Periodic task scheduling with Beat

## Deployment Checklist

- [ ] Clone both repositories
- [ ] Create `.env` from template
- [ ] Update .env with production values
- [ ] Build Docker images
- [ ] Start docker-compose services
- [ ] Run database migrations
- [ ] Create superuser account
- [ ] Verify all services are healthy
- [ ] Test login and API endpoints
- [ ] Setup SSL certificate
- [ ] Configure domain DNS
- [ ] Setup backups/monitoring
- [ ] Document passwords in secure location
- [ ] Update production settings.py
- [ ] Enable DEBUG=False
- [ ] Review security checklist

---

**Status:** Docker configuration complete  
**Environments:** Development, Production  
**Services:** 7 (postgres, redis, django, celery_worker, celery_beat, bot, frontend)
