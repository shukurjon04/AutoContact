# 🤖 SubBot — Telegram Obuna Boshqaruv Tizimi

Payme to'lov tizimi orqali ishlaydigon to'liq avtomatlashtirilgan **Telegram obuna boshqaruv boti** va **web admin panel**.

---

## 🏗 Arxitektura

```
┌─────────────────────────────────────────────────────────┐
│                        Nginx (SSL)                       │
│   /bot/webhook → bot:8080    /  → django:8000           │
└──────────────┬──────────────────────────┬───────────────┘
               │                          │
    ┌──────────▼──────────┐   ┌───────────▼──────────────┐
    │  Aiogram Bot         │   │  Django + Gunicorn        │
    │  (aiohttp :8080)     │   │  (:8000)                  │
    │  - Handlers          │   │  - Admin Panel /panel/    │
    │  - FSM States        │   │  - Payme Webhook /payme/  │
    │  - Redis FSM Storage │   │  - REST API /api/v1/      │
    └──────────────────────┘   └───────────┬──────────────┘
                                           │
              ┌────────────────────────────┼──────────────┐
              │                            │              │
    ┌─────────▼──────┐         ┌───────────▼──┐  ┌───────▼──────┐
    │  PostgreSQL     │         │    Redis      │  │ Celery Worker│
    │  (tranzaksiyalar│         │  (FSM + Cache)│  │ + Beat       │
    │   obunalar)     │         │               │  │ (har 5 daqiqa│
    └─────────────────┘         └───────────────┘  └──────────────┘
```

## 📁 Loyiha tuzilmasi

```
AutoContactBot/
├── apps/
│   ├── users/          # TelegramUser modeli
│   ├── channels/       # Channel, Tariff modellari
│   ├── subscriptions/  # Subscription, AdminAction
│   ├── payments/       # Transaction, Payme Webhook View
│   ├── notifications/  # Celery tasks, TelegramSender, Broadcast
│   ├── panel/          # Web admin panel (views, forms, templates)
│   ├── api/            # REST API (dashboard stats, broadcast status)
│   └── core/           # Health check
├── bot/
│   ├── handlers/       # /start, subscription, profile, payment
│   ├── keyboards/      # ReplyKeyboard, InlineKeyboard
│   ├── middlewares/    # DB, Throttling
│   └── services/       # Async ORM wrappers
├── config/
│   ├── settings/       # base, production, development
│   ├── celery_app.py
│   └── urls.py
├── templates/panel/    # HTML templates (Bootstrap 5)
├── nginx/              # Nginx config (SSL, proxy)
├── docker/             # Dockerfile.django, Dockerfile.bot
├── scripts/            # deploy.sh, create_superuser.sh
├── requirements/       # base, production, bot, development
└── docker-compose.yml
```

---

## 🚀 O'rnatish va Ishga Tushirish

### 1. Talablar
- Docker & Docker Compose (v2.20+)
- VPS: Ubuntu 22.04, kamida 2GB RAM
- Domain nomi (SSL uchun majburiy)

### 2. Loyihani klonlash
```bash
git clone <repo-url> AutoContactBot
cd AutoContactBot
```

### 3. Environment o'zgaruvchilarini sozlash
```bash
cp .env.example .env
nano .env
```

Quyidagi qiymatlarni to'ldiring:
| O'zgaruvchi | Tavsif |
|---|---|
| `TELEGRAM_BOT_TOKEN` | BotFather dan olingan token |
| `TELEGRAM_ADMIN_IDS` | Admin Telegram ID lari (vergul bilan) |
| `PAYME_MERCHANT_ID` | Payme Merchant ID |
| `PAYME_SECRET_KEY` | Payme Secret Key |
| `WEBHOOK_HOST` | `https://yourdomain.com` |
| `WEBHOOK_SECRET_TOKEN` | Ixtiyoriy maxfiy string (UUID tavsiya) |
| `DB_PASSWORD` | PostgreSQL paroli |
| `SECRET_KEY` | Django secret key |

### 4. Nginx domenini sozlash
```bash
# nginx/conf.d/subbot.conf faylida yourdomain.com ni o'zingiznikiga almashtiring
sed -i 's/yourdomain.com/yourdomain.com/g' nginx/conf.d/subbot.conf
```

### 5. SSL sertifikat olish (Let's Encrypt)
```bash
# Avval HTTP ni ishga tushiring (Certbot uchun)
docker compose up -d nginx postgres redis
docker compose --profile certbot run --rm certbot
```

### 6. Deploy qilish
```bash
bash scripts/deploy.sh
```

### 7. Superuser yaratish
```bash
bash scripts/create_superuser.sh
```

### 8. Admin panelga kirish
```
https://yourdomain.com/panel/
```

---

## ⚙️ Asosiy buyruqlar

```bash
# Barcha containerlarni ko'rish
docker compose ps

# Loglarni ko'rish
docker compose logs -f django
docker compose logs -f bot
docker compose logs -f celery_worker
docker compose logs -f celery_beat

# Migratsiyalar
docker compose run --rm django python manage.py migrate

# Periodic tasks sozlash
docker compose run --rm django python manage.py setup_periodic_tasks

# Django shell
docker compose run --rm django python manage.py shell

# Restart
docker compose restart django bot celery_worker
```

---

## 💳 Payme Integratsiyasi

Webhook URL: `https://yourdomain.com/payme/webhook/`

Qo'llab-quvvatlanadigan metodlar:
- `CheckPerformTransaction` — tranzaksiyani tekshirish
- `CreateTransaction` — tranzaksiya yaratish
- `PerformTransaction` — to'lovni tasdiqlash va obunani faollashtirish
- `CancelTransaction` — bekor qilish
- `CheckTransaction` — holat so'rash

Xavfsizlik:
- IP-whitelist: faqat Payme serverlaridan qabul qilinadi
- Basic Auth: `Authorization: Basic base64(merchant_id:secret_key)`

---

## 🔄 Avtomatik jarayonlar (Celery Beat)

| Task | Jadval | Vazifa |
|---|---|---|
| `check_expiring_subscriptions` | Har 5 daqiqa | 3 kun / 1 kun / 1 soat eslatmalari |
| `kick_expired_subscribers` | Har 5 daqiqa | Muddati tugaganlarni chiqarish |

---

## 🛡 Xavfsizlik

- Barcha maxfiy ma'lumotlar faqat `.env` da
- HTTPS majburiy (HTTP → HTTPS redirect)
- HSTS, X-Frame-Options, CSP headers
- Payme webhook IP-filtering
- Django session auth (admin panel)
- Rate limiting (bot: 0.5 msg/sec per user)

---

## 📊 Admin Panel

| Sahifa | URL | Tavsif |
|---|---|---|
| Dashboard | `/panel/` | Statistika, daromad |
| Kanallar | `/panel/channels/` | Kanal va tarif boshqaruvi |
| Foydalanuvchilar | `/panel/users/` | Obunalarni boshqarish |
| Tranzaksiyalar | `/panel/transactions/` | To'lovlar tarixi, CSV export |
| Broadcast | `/panel/broadcast/` | Ommaviy xabarnoma |

---

## 🐛 Debugging

```bash
# Bot polling rejimida ishlatish (development)
BOT_MODE=polling python -m bot.main

# Celery worker debug
celery -A config.celery_app worker --loglevel=debug

# Django dev server
python manage.py runserver --settings=config.settings.development
```
