#!/bin/bash
# ==============================================================================
# AutoContactBot — Production Deployment Script
# Ubuntu 22.04+ VPS uchun
#
# Ishlatish:
#   chmod +x scripts/deploy.sh && ./scripts/deploy.sh
#
# Bu script:
#   1. .env tekshiradi
#   2. Docker imagelarni build qiladi
#   3. Barcha servislarni ishga tushiradi
#   4. SSL sertifikat avtomatik olinadi (Nginx entrypoint orqali)
#   5. Health check bajaradi
# ==============================================================================
set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

log_info()  { echo -e "${CYAN}[INFO]${NC}  $*"; }
log_ok()    { echo -e "${GREEN}[OK]${NC}    $*"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $*"; }

echo ""
echo "============================================"
echo "  AutoContactBot — Production Deployment"
echo "============================================"
echo ""

# ── Pre-flight checks ────────────────────────────────────────────────────────

# .env fayl bormi?
if [ ! -f ".env" ]; then
    log_error ".env fayli topilmadi!"
    echo "  Avval .env faylini yarating:"
    echo "    cp .env.example .env && nano .env"
    exit 1
fi

# Placeholder qiymatlar qolganmi?
DOMAIN=$(grep -E '^DOMAIN=' .env | cut -d= -f2)
BOT_TOKEN=$(grep -E '^TELEGRAM_BOT_TOKEN=' .env | cut -d= -f2)

if [ "${DOMAIN}" = "yourdomain.com" ]; then
    log_error ".env da DOMAIN hali placeholder! Haqiqiy domainigizni yozing."
    exit 1
fi

if [ "${BOT_TOKEN}" = "your_bot_token_here" ]; then
    log_error ".env da TELEGRAM_BOT_TOKEN hali placeholder! BotFather'dan olingan tokenni yozing."
    exit 1
fi

log_ok ".env fayl tekshirildi. Domain: ${DOMAIN}"

# Docker ishlayaptimi?
if ! docker info &>/dev/null; then
    log_error "Docker ishlamayapti. Docker Engine o'rnatilganini tekshiring."
    exit 1
fi
log_ok "Docker Engine ishlayapti."

# ── Build & Deploy ───────────────────────────────────────────────────────────

log_info "[1/5] Docker imagelarni build qilish..."
docker compose build --no-cache

log_info "[2/5] Eski containerlarni to'xtatish..."
docker compose down --remove-orphans 2>/dev/null || true

log_info "[3/5] Database va cache servislarni ishga tushirish..."
docker compose up -d postgres redis

log_info "       PostgreSQL va Redis tayyor bo'lguncha kutilmoqda..."
sleep 15

# Healthcheck kutish
for i in $(seq 1 30); do
    if docker compose exec postgres pg_isready -U "$(grep -E '^DB_USER=' .env | cut -d= -f2)" &>/dev/null; then
        log_ok "PostgreSQL tayyor."
        break
    fi
    sleep 2
done

log_info "[4/5] Barcha servislarni ishga tushirish..."
docker compose up -d

log_info "[5/5] Servislar tayyor bo'lishini kutish..."
sleep 30

# ── Health checks ────────────────────────────────────────────────────────────

echo ""
echo "────────────────────────────────────────────"
echo "  Servis holatlari"
echo "────────────────────────────────────────────"

docker compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "────────────────────────────────────────────"
echo "  SSL sertifikat holati"
echo "────────────────────────────────────────────"

# Nginx loglaridan SSL holatini tekshirish
if docker compose logs nginx 2>/dev/null | grep -q "SSL certificate obtained"; then
    log_ok "Let's Encrypt SSL sertifikat muvaffaqiyatli olindi!"
elif docker compose logs nginx 2>/dev/null | grep -q "Using existing certificates"; then
    log_ok "Mavjud SSL sertifikat ishlatilmoqda."
elif docker compose logs nginx 2>/dev/null | grep -q "Certbot failed"; then
    log_warn "SSL sertifikat olinmadi. DNS tekshiring yoki qo'lda urinib ko'ring:"
    echo "  docker compose exec nginx certbot certonly --webroot -w /var/www/certbot -d ${DOMAIN}"
else
    log_warn "SSL holati aniqlanmadi. Nginx loglarini tekshiring:"
    echo "  docker compose logs nginx"
fi

echo ""
echo "============================================"
echo "  ✅ Deployment yakunlandi!"
echo "============================================"
echo ""
echo "  🌐 Health check : https://${DOMAIN}/health/"
echo "  🔑 Admin panel  : https://${DOMAIN}/panel/"
echo "  🤖 Bot          : @YourBotUsername ga /start yuboring"
echo ""
echo "  📋 Loglarni ko'rish:"
echo "    docker compose logs -f django"
echo "    docker compose logs -f bot"
echo "    docker compose logs -f nginx"
echo "    docker compose logs -f celery_worker"
echo ""
