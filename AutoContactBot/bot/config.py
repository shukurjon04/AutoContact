"""
Bot configuration — reads environment variables directly via decouple.
Used when running the bot process (Django settings are also loaded via manage.py setup).
"""
from decouple import config, Csv

BOT_TOKEN: str = config("TELEGRAM_BOT_TOKEN")
ADMIN_IDS: list[int] = config("TELEGRAM_ADMIN_IDS", cast=Csv(int))
REDIS_URL: str = config("REDIS_URL", default="redis://redis:6379/0")
WEBHOOK_HOST: str = config("WEBHOOK_HOST", default="")
WEBHOOK_PATH: str = config("WEBHOOK_PATH", default="/bot/webhook")
WEBHOOK_SECRET_TOKEN: str = config("WEBHOOK_SECRET_TOKEN", default="")
BOT_MODE: str = config("BOT_MODE", default="webhook")
