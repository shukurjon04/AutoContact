#!/bin/bash
# Admin panel uchun superuser yaratish
set -e

echo "Django superuser yaratilmoqda..."
docker compose run --rm django python manage.py createsuperuser
echo "Superuser muvaffaqiyatli yaratildi."
