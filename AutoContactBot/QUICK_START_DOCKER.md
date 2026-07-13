# 🚀 SubBot - ONE COMMAND START GUIDE

## ⚡ FASTEST START (Bitta Buyruq!)

```bash
cd AutoContactBot
cp .env.example .env
docker compose up
```

**Tayyor!** ✅

```
🌐 Frontend:      http://localhost
📱 Backend API:   http://localhost/api/v1/
🔑 Admin:         http://localhost/django-admin/
💚 Health:        http://localhost/health/
```

---

## 📋 STEP-BY-STEP (Birinchi Marta)

### 1️⃣ **Prepare**

```bash
# Backend directory-ga o'tish
cd /path/to/AutoContactBot

# Frontend clone qilish (agar bo'lmasa)
git clone <frontend-repo> ../AutoContactBot-Frontend

# Environment file
cp .env.example .env

# IMPORTANT: .env ni tekshiring va update qiling:
nano .env
```

**.env Example (Development):**
```bash
DEBUG=True
DB_NAME=subscription_bot_db
DB_USER=subscription_bot_user
DB_PASSWORD=dev_password
SECRET_KEY=dev-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost
TELEGRAM_BOT_TOKEN=your_token_here
```

### 2️⃣ **Start Everything**

```bash
docker compose up
```

**Kutish:** Database va services tayyor bo'lguncha (1-2 minut)

```
✅ postgres      - Running
✅ redis         - Running
✅ django        - Running (migrations avtomatik qilinadi)
✅ celery_worker - Running
✅ celery_beat   - Running
✅ bot           - Running
✅ frontend      - Running (Nginx)
```

### 3️⃣ **Create Admin User** (OPTIONAL)

New terminal:
```bash
cd AutoContactBot
docker compose exec django python manage.py createsuperuser
```

Ko'rsatmalarni kuzatib admin foydalanuvchi yarating.

### 4️⃣ **Access Services**

| Service | URL | Credentials |
|---------|-----|-------------|
| **Frontend** | http://localhost | Admin username/password |
| **API Docs** | http://localhost/api/v1/ | Same |
| **Django Admin** | http://localhost/django-admin/ | Same |
| **Health Check** | http://localhost/health/ | - |
| **Database** | localhost:5432 | user/password from .env |
| **Redis** | localhost:6379 | - |

---

## 🛑 **STOP**

```bash
docker compose down
```

---

## 📊 **COMMON COMMANDS**

```bash
# Logs ko'rish
docker compose logs -f                  # Barcha logs
docker compose logs -f django           # Faqat Django
docker compose logs -f celery_worker    # Faqat Celery

# Services status
docker compose ps

# Database shell
docker compose exec django python manage.py shell

# Migrations
docker compose exec django python manage.py makemigrations
docker compose exec django python manage.py migrate

# Static files
docker compose exec django python manage.py collectstatic

# Restart service
docker compose restart django
docker compose restart celery_worker
docker compose restart frontend

# Rebuild images (after code change)
docker compose build
docker compose up
```

---

## 🔧 **PRODUCTION SETUP**

```bash
# Production .env
cp .env.example .env
nano .env

# Update:
DEBUG=False
SECRET_KEY=very-long-secret-key-min-50-chars
DB_PASSWORD=strong-password-min-32-chars
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CORS_ALLOWED_ORIGINS=https://yourdomain.com
DOMAIN=yourdomain.com

# Start in background
docker compose up -d

# Check status
docker compose ps

# Logs
docker compose logs -f django
```

---

## ⚠️ **TROUBLESHOOTING**

### "Connection refused"
```bash
docker compose down
docker compose up
```

### "Port already in use"
```bash
# Check what's using ports
lsof -i :80
lsof -i :5432
lsof -i :6379

# Or change ports in docker-compose.yml
# ports:
#   - "8080:80"  # Frontend
#   - "5433:5432"  # Database
```

### "Database won't start"
```bash
docker compose logs postgres
docker volume rm subbot_postgres_data
docker compose up
```

### "Frontend not showing"
```bash
docker compose logs frontend
docker compose restart frontend
curl http://localhost  # Test
```

### "API returns 502"
```bash
docker compose logs django
docker compose restart django
```

---

## 🔍 **VERIFY EVERYTHING**

```bash
# 1. Check containers
docker compose ps
# All should be "Up" status

# 2. Check health
curl http://localhost/health/
# Should return: {"status": "ok"}

# 3. Check API
curl http://localhost/api/v1/users/ -H "Authorization: Bearer TOKEN"
# Should return user list

# 4. Check frontend
curl http://localhost
# Should return HTML

# 5. Check database
docker compose exec postgres psql -U subscription_bot_user -d subscription_bot_db -c "SELECT version();"
# Should show PostgreSQL version
```

---

## 📱 **LOGIN TEST**

1. Open http://localhost
2. Username: `admin` (or createsuperuser nomingiz)
3. Password: (superuser parolingiz)
4. Click "Kirish" (Sign In)
5. Should see dashboard

---

## 🚀 **NEXT STEPS**

- ✅ Backend API ready
- ✅ Frontend running
- ✅ Database configured
- ✅ Celery workers active
- ⏭️ Create admin user
- ⏭️ Add channels/tariffs
- ⏭️ Configure Telegram bot
- ⏭️ Setup Payme integration

---

## 📚 **MORE INFO**

See detailed guides:
- `API_SETUP.md` — API endpoints documentation
- `FRONTEND_SETUP.md` — Angular frontend setup
- `DOCKER_DEPLOYMENT.md` — Advanced Docker & production
- `IMPLEMENTATION_SUMMARY.md` — Full project overview

---

## 💡 **TIPS**

1. **First time slow?** Database initializing, be patient (2-3 min)
2. **Code changes?** Services auto-reload for development
3. **Production?** Change `DEBUG=False`, set strong passwords
4. **Logs too much?** Run in background: `docker compose up -d`
5. **Database backup?** `docker compose exec postgres pg_dump ...`

---

**Hammasi tayyor! Enjoy! 🎉**

Questions? Check documentation files or see logs!
