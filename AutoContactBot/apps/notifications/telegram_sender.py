"""
TelegramSender — async helper that uses the Bot API directly via httpx.
Used by Celery tasks (sync context calling asyncio.run).
"""
import logging
from datetime import datetime

import httpx
from django.conf import settings

logger = logging.getLogger(__name__)

BOT_API_BASE = "https://api.telegram.org/bot{token}/{method}"
TIMEOUT = 15.0


class TelegramSender:
    """Telegram Bot API wrapper for Celery tasks."""

    def __init__(self):
        self.token = settings.TELEGRAM_BOT_TOKEN
        self.base_url = f"https://api.telegram.org/bot{self.token}"

    async def _post(self, method: str, payload: dict) -> dict | None:
        url = f"{self.base_url}/{method}"
        try:
            async with httpx.AsyncClient(timeout=TIMEOUT) as client:
                resp = await client.post(url, json=payload)
                data = resp.json()
                if not data.get("ok"):
                    logger.error("Telegram API error [%s]: %s", method, data)
                    return None
                return data.get("result")
        except Exception:
            logger.exception("Telegram API request failed: %s", method)
            return None

    async def create_invite_link(self, channel_id: int) -> str | None:
        """Bir martalik, 24 soatlik invite link yaratadi."""
        from django.utils import timezone
        import time
        expire_ts = int(time.time()) + 86400  # 24 soat

        result = await self._post("createChatInviteLink", {
            "chat_id": channel_id,
            "member_limit": 1,
            "expire_date": expire_ts,
            "creates_join_request": False,
        })
        return result.get("invite_link") if result else None

    async def send_invite_link(
        self,
        user_telegram_id: int,
        channel_name: str,
        invite_link: str,
        end_date: datetime,
    ) -> bool:
        """Foydalanuvchiga invite link yuboradi."""
        text = (
            f"✅ <b>To'lov qabul qilindi!</b>\n\n"
            f"📢 Kanal: <b>{channel_name}</b>\n"
            f"📅 Obuna tugash sanasi: <b>{end_date.strftime('%d.%m.%Y')}</b>\n\n"
            f"🔗 Quyidagi havola orqali guruhga qo'shiling:\n{invite_link}\n\n"
            f"⚠️ <i>Havola faqat bir marta ishlatiladi va 24 soat ichida eskiradi.</i>"
        )
        result = await self._post("sendMessage", {
            "chat_id": user_telegram_id,
            "text": text,
            "parse_mode": "HTML",
        })
        return result is not None

    async def send_subscription_extended(
        self,
        user_telegram_id: int,
        channel_name: str,
        end_date: datetime,
    ) -> bool:
        text = (
            f"✅ <b>Obunangiz uzaytirildi!</b>\n\n"
            f"📢 Kanal: <b>{channel_name}</b>\n"
            f"📅 Yangi tugash sanasi: <b>{end_date.strftime('%d.%m.%Y')}</b>"
        )
        result = await self._post("sendMessage", {
            "chat_id": user_telegram_id,
            "text": text,
            "parse_mode": "HTML",
        })
        return result is not None

    async def send_expiry_reminder(
        self,
        user_telegram_id: int,
        channel_name: str,
        end_date: datetime,
        time_left_label: str,
        subscription_id: str,
    ) -> bool:
        """Obuna tugash eslatmasi."""
        text = (
            f"⏰ <b>Eslatma!</b>\n\n"
            f"📢 <b>{channel_name}</b> kanalidagi obunangiz "
            f"<b>{time_left_label}</b> ichida tugaydi.\n"
            f"📅 Tugash sanasi: <b>{end_date.strftime('%d.%m.%Y %H:%M')}</b>\n\n"
            f"Obunangizni uzaytirish uchun /start buyrug'ini yuboring."
        )
        result = await self._post("sendMessage", {
            "chat_id": user_telegram_id,
            "text": text,
            "parse_mode": "HTML",
        })
        return result is not None

    async def send_subscription_expired(
        self,
        user_telegram_id: int,
        channel_name: str,
        subscription_id: str,
    ) -> bool:
        """Obuna tugaganini xabar qiladi."""
        text = (
            f"❌ <b>Obunangiz tugadi!</b>\n\n"
            f"📢 <b>{channel_name}</b> kanaliga kirishingiz to'xtatildi.\n\n"
            f"Qayta obuna bo'lish uchun /start buyrug'ini yuboring."
        )
        result = await self._post("sendMessage", {
            "chat_id": user_telegram_id,
            "text": text,
            "parse_mode": "HTML",
        })
        return result is not None

    async def kick_user(self, channel_id: int, user_id: int) -> bool:
        """Foydalanuvchini kanaldan chiqaradi (ban + unban)."""
        # Ban
        ban_result = await self._post("banChatMember", {
            "chat_id": channel_id,
            "user_id": user_id,
        })
        if not ban_result:
            logger.error("Failed to ban user %s from channel %s", user_id, channel_id)
            return False

        # Unban (keyinchalik qayta qo'shilishi mumkin bo'lsin)
        await self._post("unbanChatMember", {
            "chat_id": channel_id,
            "user_id": user_id,
            "only_if_banned": True,
        })
        logger.info("User %s kicked from channel %s", user_id, channel_id)
        return True

    async def send_broadcast_message(
        self,
        user_telegram_id: int,
        text: str,
        photo_url: str | None = None,
    ) -> bool:
        if photo_url:
            result = await self._post("sendPhoto", {
                "chat_id": user_telegram_id,
                "photo": photo_url,
                "caption": text,
                "parse_mode": "HTML",
            })
        else:
            result = await self._post("sendMessage", {
                "chat_id": user_telegram_id,
                "text": text,
                "parse_mode": "HTML",
            })
        return result is not None
