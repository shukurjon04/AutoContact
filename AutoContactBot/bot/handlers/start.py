"""
/start command handler — registers user and shows main menu.
"""
import logging
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from bot.keyboards.main_menu import get_main_menu_keyboard
from bot.services.user_service import get_or_create_user

logger = logging.getLogger(__name__)
router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    tg_user = message.from_user
    if not tg_user:
        return

    try:
        user, is_new = await get_or_create_user(
            telegram_id=tg_user.id,
            first_name=tg_user.first_name or "",
            last_name=tg_user.last_name or "",
            username=tg_user.username,
            language_code=tg_user.language_code or "uz",
        )
    except Exception:
        logger.exception("Error registering user %s", tg_user.id)
        await message.answer("❌ Xatolik yuz berdi. Iltimos qayta urinib ko'ring.")
        return

    greeting = "Xush kelibsiz" if is_new else "Qaytib keldingiz"
    name = tg_user.first_name or "Do'st"

    text = (
        f"👋 <b>{greeting}, {name}!</b>\n\n"
        f"Bu bot orqali siz yopiq guruh va kanallarga obuna bo'lishingiz mumkin.\n\n"
        f"Quyidagi menyudan kerakli bo'limni tanlang:"
    )

    await message.answer(text, reply_markup=get_main_menu_keyboard())
    logger.info("User %s started bot (new=%s)", tg_user.id, is_new)
