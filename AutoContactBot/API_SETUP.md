# 🚀 Django REST API Setup — 1-qadam Tayyor!

## ✅ Yaratilgan Modullar

### Serializers (`apps/api/serializers.py`)
Barcha Django modellari uchun DRF serializers:
- `TelegramUserSerializer` — Foydalanuvchilar ma'lumotlari
- `ChannelSerializer` / `ChannelDetailSerializer` — Kanallar
- `TariffSerializer` — Tarifflar 
- `SubscriptionListSerializer` / `SubscriptionDetailSerializer` — Obunalar
- `AdminActionSerializer` — Admin amallar logi
- `TransactionListSerializer` / `TransactionDetailSerializer` — Tranzaksiyalar
- `BroadcastListSerializer` / `BroadcastDetailSerializer` — Broadcastlar
- `BroadcastRecipientSerializer` — Qabul qiluvchilar
- `PaymentSettingsSerializer` — To'lov sozlamalari
- `DashboardStatsSerializer` — Dashboard statistikasi

### ViewSets (`apps/api/views.py`)
RESTful API endpoints — barcha CRUD operatsiyalar:

#### 🔐 Authentication
- `ProfileView` — Hozirgi foydalanuvchi ma'lumoti
- `/api/v1/auth/token/` — JWT token olish (POST)
- `/api/v1/auth/token/refresh/` — Refresh token (POST)

#### 👥 Telegram Users
- `TelegramUserViewSet` — Foydalanuvchilar
  - `GET /users/` — Ro'yxat (filter, search, paginate)
  - `GET /users/{id}/` — Detallar
  - `PATCH /users/{id}/` — O'zgartirish
  - `DELETE /users/{id}/` — O'chirish
  - `POST /users/{id}/block/` — Blok qilish
  - `POST /users/{id}/unblock/` — Blokdan chiqarish

#### 📺 Channels & Tariffs
- `ChannelViewSet` — Kanallar
  - `GET /channels/` — Ro'yxat
  - `POST /channels/` — Yaratish
  - `GET /channels/{id}/` — Detallar
  - `PATCH /channels/{id}/` — O'zgartirish
  - `DELETE /channels/{id}/` — O'chirish
  - `POST /channels/{id}/deactivate/` — Deaktivatsiya

- `TariffViewSet` — Tariflar
  - `GET /tariffs/` — Ro'yxat
  - `POST /tariffs/` — Yaratish
  - `GET /tariffs/{id}/` — Detallar
  - `PATCH /tariffs/{id}/` — O'zgartirish
  - `DELETE /tariffs/{id}/` — O'chirish

#### 📋 Subscriptions
- `SubscriptionViewSet` — Obunalar
  - `GET /subscriptions/` — Ro'yxat (filter by user, channel, status)
  - `POST /subscriptions/` — Yaratish
  - `GET /subscriptions/{id}/` — Detallar
  - `POST /subscriptions/{id}/extend/` — Muddatni uzaytirish
  - `POST /subscriptions/{id}/cancel/` — Bekor qilish

#### 💰 Payments
- `TransactionViewSet` — Tranzaksiyalar
  - `GET /transactions/` — Ro'yxat
  - `GET /transactions/{id}/` — Detallar
  - `POST /transactions/{id}/approve/` — Tasdiqlash
  - `POST /transactions/{id}/reject/` — Rad qilish
  - `GET /transactions/stats/` — Statistika

#### 📢 Broadcasts
- `BroadcastViewSet` — Xabarnomalar
  - `GET /broadcasts/` — Ro'yxat
  - `POST /broadcasts/` — Yaratish
  - `GET /broadcasts/{id}/` — Detallar
  - `POST /broadcasts/{id}/launch/` — Yuborish
  - `GET /broadcasts/{id}/recipients/` — Qabul qiluvchilar

#### 📊 Dashboard
- `DashboardStatsView` — Dashboard statistikasi
  - `GET /dashboard/stats/` — Barcha stats

### Supporting Files
- `permissions.py` — Custom permissions (IsAdmin, IsAdminOrReadOnly)
- `pagination.py` — Pagination classes
- `filters.py` — Advanced filtering untuk complex queries
- `urls.py` — URL routing (register barcha endpoints)

## 🔧 Settings Configuration

### Django Settings (`config/settings/base.py`)
Quyidagilar qo'shildi:

**INSTALLED_APPS:**
```python
"django_filters",
```

**MIDDLEWARE:**
```python
"corsheaders.middleware.CorsMiddleware",  # Already there
```

**DRF Configuration:**
```python
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    # ... rest of config
}
```

**JWT Configuration:**
```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'ALGORITHM': 'HS256',
    # ... rest of config
}
```

**CORS Configuration:**
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:4200",     # Development
    "https://yourdomain.com",    # Production
]
CORS_ALLOW_CREDENTIALS = True
```

## 📦 New Requirements

Qo'shilgan dependencies (`requirements/base.txt`):
```
django-filter==24.1
django-cors-headers==4.3.1
```

## 🧪 Testing API Endpoints

### 1. Token Olish
```bash
curl -X POST http://localhost:8000/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "your_password"
  }'
```

Response:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### 2. Users Ro'yxati
```bash
curl -X GET "http://localhost:8000/api/v1/users/?page=1" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 3. Channel Yaratish
```bash
curl -X POST http://localhost:8000/api/v1/channels/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Channel Name",
    "telegram_id": -1001234567890,
    "description": "Channel description"
  }'
```

### 4. Dashboard Stats
```bash
curl -X GET http://localhost:8000/api/v1/dashboard/stats/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 🔄 Workflow

### Authentication Flow
1. **Frontend** sends login credentials to `/api/v1/auth/token/`
2. **Backend** returns `access_token` (1 hour) va `refresh_token` (7 days)
3. **Frontend** sends `Authorization: Bearer <access_token>` header har bir requestda
4. Token expiratsiya bo'lsa, frontend refresh token bilan yangi access token oladi

### API Request Sequence
```
1. Frontend → POST /api/v1/auth/token/
2. Backend → returns { access, refresh }
3. Frontend → GET /api/v1/users/ with Authorization header
4. Backend → returns paginated user list
5. Frontend → displays users in Angular
```

## 📋 API Endpoints Summary

### Base URL
```
http://localhost:8000/api/v1/
```

### Endpoints Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| **AUTH** |
| POST | `/auth/token/` | Get JWT token |
| POST | `/auth/token/refresh/` | Refresh JWT token |
| GET | `/auth/me/` | Get current user |
| **USERS** |
| GET | `/users/` | List users |
| GET | `/users/{id}/` | User details |
| PATCH | `/users/{id}/` | Update user |
| DELETE | `/users/{id}/` | Delete user |
| POST | `/users/{id}/block/` | Block user |
| POST | `/users/{id}/unblock/` | Unblock user |
| **CHANNELS** |
| GET | `/channels/` | List channels |
| POST | `/channels/` | Create channel |
| GET | `/channels/{id}/` | Channel details |
| PATCH | `/channels/{id}/` | Update channel |
| DELETE | `/channels/{id}/` | Delete channel |
| POST | `/channels/{id}/deactivate/` | Deactivate channel |
| **TARIFFS** |
| GET | `/tariffs/` | List tariffs |
| POST | `/tariffs/` | Create tariff |
| GET | `/tariffs/{id}/` | Tariff details |
| PATCH | `/tariffs/{id}/` | Update tariff |
| DELETE | `/tariffs/{id}/` | Delete tariff |
| **SUBSCRIPTIONS** |
| GET | `/subscriptions/` | List subscriptions |
| POST | `/subscriptions/` | Create subscription |
| GET | `/subscriptions/{id}/` | Subscription details |
| POST | `/subscriptions/{id}/extend/` | Extend subscription |
| POST | `/subscriptions/{id}/cancel/` | Cancel subscription |
| **TRANSACTIONS** |
| GET | `/transactions/` | List transactions |
| GET | `/transactions/{id}/` | Transaction details |
| POST | `/transactions/{id}/approve/` | Approve transaction |
| POST | `/transactions/{id}/reject/` | Reject transaction |
| GET | `/transactions/stats/` | Transaction statistics |
| **BROADCASTS** |
| GET | `/broadcasts/` | List broadcasts |
| POST | `/broadcasts/` | Create broadcast |
| GET | `/broadcasts/{id}/` | Broadcast details |
| POST | `/broadcasts/{id}/launch/` | Launch broadcast |
| GET | `/broadcasts/{id}/recipients/` | Get recipients |
| **DASHBOARD** |
| GET | `/dashboard/stats/` | Dashboard statistics |
| **SETTINGS** |
| GET | `/payment-settings/` | Get payment settings |
| PUT | `/payment-settings/` | Update payment settings |

## 🔒 Authentication & Permissions

- All endpoints require `Authentication: Bearer <token>`
- Only **Admin users** (is_staff=True) can access API
- Token lifetime: 1 hour (refresh with refresh_token)
- CORS enabled for Angular frontend (localhost:4200)

## 🚀 Next Steps (2-qadam)

**Angular Frontend** yasash:
1. Angular project setup
2. HTTP client + interceptors
3. Auth service
4. CRUD pages for all resources
5. Dashboard with charts
6. Uzbek language (i18n)

---

**Status:** ✅ Backend API Ready  
**Modified:** 2026-07-13  
**Author:** Claude Code
