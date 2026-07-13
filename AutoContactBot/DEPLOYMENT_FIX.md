# 🔧 Deployment Configuration Fix - CSRF 403 Error

## 🚨 Problem
Production serveri (`bot.robotronix.uz`) ga kirish urinayotganda:
```
403 Forbidden - CSRF token missing or incorrect
```

## ✅ Solution

### Step 1: Environment Variables (.env) Update

`.env` faylingizga quyidagilarni qo'shing yoki o'zgartiring:

```bash
# DJANGO Configuration
ALLOWED_HOSTS=bot.robotronix.uz,www.bot.robotronix.uz
CSRF_TRUSTED_ORIGINS=https://bot.robotronix.uz,https://www.bot.robotronix.uz
```

### Step 2: Environment Variable Description

| Variable | Value | Description |
|----------|-------|-------------|
| `ALLOWED_HOSTS` | `bot.robotronix.uz,www.bot.robotronix.uz` | Django tomonidan ruxsat etilgan domenlar |
| `CSRF_TRUSTED_ORIGINS` | `https://bot.robotronix.uz,https://www.bot.robotronix.uz` | CSRF validatsiyasi uchun ishonchli domenlar |

### Step 3: Complete .env Example

```bash
# ============================================
# DOMAIN & SSL
# ============================================
DOMAIN=bot.robotronix.uz
CERTBOT_EMAIL=admin@robotronix.uz

# ============================================
# DJANGO
# ============================================
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=bot.robotronix.uz,www.bot.robotronix.uz
CSRF_TRUSTED_ORIGINS=https://bot.robotronix.uz,https://www.bot.robotronix.uz
DJANGO_SETTINGS_MODULE=config.settings.production

# ... (boshqa settings)
```

---

## 🔐 Security Settings (Production)

Quyidagi xavfsizlik sozlamalari avvaldan **config/settings/production.py** da o'rnatilgan:

```python
# SSL/HTTPS
SECURE_SSL_REDIRECT = True              # HTTP → HTTPS yo'naltirish
SESSION_COOKIE_SECURE = True            # Cookie faqat HTTPS orqali
CSRF_COOKIE_SECURE = True               # CSRF cookie faqat HTTPS orqali
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# HSTS (HTTP Strict Transport Security)
SECURE_HSTS_SECONDS = 31536000          # 1 yil
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Security Headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
```

---

## 📋 Deployment Checklist

Serverni deploy qilishdan oldin quyidagilarni tekshiring:

- [ ] ✅ `.env` faylini yangilangiz (ALLOWED_HOSTS, CSRF_TRUSTED_ORIGINS)
- [ ] ✅ Django static files collect qiling: `python manage.py collectstatic --noinput`
- [ ] ✅ Database migrations apply qiling: `python manage.py migrate`
- [ ] ✅ Django serverni restart qiling
- [ ] ✅ Nginx reverse proxy to'g'ri konfiguratsiya qilingan (X-Forwarded-Proto header)
- [ ] ✅ SSL sertifikat o'rnatilgan (Let's Encrypt)
- [ ] ✅ Cookies 3rd-party ga yuborish uchun: `SameSite=None; Secure` o'rnatilgan

---

## 🌐 Nginx Configuration Example

Nginx da X-Forwarded-Proto header o'rnatish:

```nginx
upstream django {
    server django:8000;
}

server {
    listen 80;
    server_name bot.robotronix.uz www.bot.robotronix.uz;
    
    # HTTP → HTTPS redirect
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name bot.robotronix.uz www.bot.robotronix.uz;

    ssl_certificate /etc/letsencrypt/live/bot.robotronix.uz/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/bot.robotronix.uz/privkey.pem;

    location / {
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;  # ⭐ IMPORTANT
        proxy_redirect off;
    }

    location /static/ {
        alias /app/static/;
        expires 30d;
    }

    location /media/ {
        alias /app/media/;
        expires 7d;
    }
}
```

---

## 🧪 Testing

### Test 1: CSRF Token Check
```bash
# Panel login sahifasini tekshiring
curl -L https://bot.robotronix.uz/panel/login/

# Javobda CSRF token bo'lishi kerak:
# <input type="hidden" name="csrfmiddlewaretoken" value="...">
```

### Test 2: Login Test
```bash
# Login qilishni sinab ko'ring (bash/curl bilan)
curl -X POST https://bot.robotronix.uz/panel/login/ \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "Origin: https://bot.robotronix.uz" \
  -c cookies.txt \
  -d "username=admin&password=yourpassword"
```

### Test 3: Django Logs Check
```bash
# Xatalari ko'rish uchun Django logs'ni tekshiring
docker logs <django_container_name>
tail -f /var/log/django/error.log
```

---

## 🔍 Debugging Tips

### If Still Getting 403 Error:

**1. Check ALLOWED_HOSTS:**
```bash
# Django shell'da tekshiring
python manage.py shell
>>> from django.conf import settings
>>> print(settings.ALLOWED_HOSTS)
['bot.robotronix.uz', 'www.bot.robotronix.uz', ...]
```

**2. Check CSRF_TRUSTED_ORIGINS:**
```bash
>>> print(settings.CSRF_TRUSTED_ORIGINS)
['https://bot.robotronix.uz', 'https://www.bot.robotronix.uz']
```

**3. Check Nginx Headers:**
```bash
# Nginx tomonidan yuborilayotgan headersni tekshiring
curl -vv https://bot.robotronix.uz/panel/login/ 2>&1 | grep -i "x-forwarded"
```

**4. Check Django Logs:**
```bash
# CSRF xatolarini ko'rish uchun DEBUG=True qiling vaqtinchalik
DEBUG=True python manage.py runserver
```

---

## 🚀 After Fix

### Verify Login Works
1. Open: `https://bot.robotronix.uz/panel/login/`
2. Enter credentials
3. Click "Tizimga kirish"
4. Should redirect to dashboard

### Verify Admin Panel
1. Sidebar should load
2. All menu items should work
3. No CSRF errors in console

---

## 📝 Reference

### Files Modified:
- ✅ `config/settings/production.py` - Added CSRF_TRUSTED_ORIGINS
- ✅ `.env.example` - Added CSRF_TRUSTED_ORIGINS variable
- ✅ `DEPLOYMENT_FIX.md` - This file

### No Changes Needed For:
- ✓ Templates (login.html correct)
- ✓ Views
- ✓ Database
- ✓ Dependencies

---

## 💡 Important Notes

### Why This Happens?
Django production mode engages:
1. `SECURE_SSL_REDIRECT = True` - All requests must be HTTPS
2. `CSRF_COOKIE_SECURE = True` - Cookies sent only on HTTPS
3. `ALLOWED_HOSTS` check - Domain must be explicitly allowed
4. CSRF validation - Token + domain must match

### Why It Works Now?
- ✅ ALLOWED_HOSTS includes your production domain
- ✅ CSRF_TRUSTED_ORIGINS configured correctly
- ✅ Nginx sending correct X-Forwarded-Proto header
- ✅ Session cookies marked as Secure (HTTPS only)

---

## ⏭️ Next Steps

1. **Update .env on server** with CSRF_TRUSTED_ORIGINS
2. **Restart Django service**: `docker-compose restart django` or `systemctl restart django`
3. **Test login** at `https://bot.robotronix.uz/panel/login/`
4. **Verify sidebar** opens correctly
5. **Check admin**: `https://bot.robotronix.uz/admin/`

---

**Generated:** 2026-07-13
**Status:** ✅ Ready to Apply
**Impact:** Low Risk - Configuration only, no code changes
