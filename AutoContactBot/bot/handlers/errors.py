"""
Global error handler — catches unhandled exceptions in bot handlers.
"""
import logging
from aiogram import Router
from aiogram.types import Update, ErrorEvent
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest

logger = logging.getLogger(__name__)
router = Router(name="errors")


@router.errors()
async def global_error_handler(event: ErrorEvent) -> bool:
    """
    Barcha handlerlardan o'tib ketgan xatoliklarni ushlab qoladi.
    Returns True — xatolik qayta urinish uchun propagate qilinmaydi.
    """
    exception = event.exception
    update: Update | None = event.update

    # Foydalanuvchi botni bloklagan — TelegramForbiddenError
    if isinstance(exception, TelegramForbiddenError):
        if update and update.message:
            user_id = update.message.from_user.id if update.message.from_user else None
            if user_id:
                await _mark_user_blocked(user_id)
        logger.info("User blocked the bot: %s", exception)
        return True

    # Bad request — xabar o'chirilgan yoki boshqa Telegram xatoligi
    if isinstance(exception, TelegramBadRequest):
        logger.warning("Telegram BadRequest: %s", exception)
        return True

    # Boshqa xatoliklar
    logger.exception(
        "Unhandled exception in bot handler. Update: %s",
        update.model_dump_json() if update else "N/A",
        exc_info=exception,
    )
    return True


async def _mark_user_blocked(telegram_id: int) -> None:
    """Foydalanuvchini bazada bot_blocked=True deb belgilaydi."""
    try:
        from asgiref.sync import sync_to_async
        from apps.users.models import TelegramUser

        @sync_to_async
        def _update():
            TelegramUser.objects.filter(telegram_id=telegram_id).update(is_bot_blocked=True)

        await _update()
        logger.info("Marked user %s as bot_blocked", telegram_id)
    except Exception:
        logger.exception("Failed to mark user %s as bot_blocked", telegram_id)
