"""
Payment status check handler.
"""
import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery

from bot.services.payment_service import check_payment_status

logger = logging.getLogger(__name__)
router = Router(name="payment")


@router.callback_query(F.data.startswith("check_payment:"))
async def check_payment(callback: CallbackQuery) -> None:
    transaction_id = callback.data.split(":")[1]
    await callback.answer("⏳ To'lov holati tekshirilmoqda...")

    status = await check_payment_status(transaction_id)

    if status == "paid":
        await callback.message.edit_text(
            "✅ <b>To'lov muvaffaqiyatli!</b>\n\n"
            "Obunangiz faollashtirildi. Guruhga qo'shilish havolasi yuborildi.",
        )
    elif status == "pending":
        await callback.answer(
            "⏳ To'lov hali amalga oshmagan. Iltimos to'lovni yakunlang.",
            show_alert=True,
        )
    elif status == "cancelled":
        await callback.message.edit_text(
            "❌ <b>To'lov bekor qilindi.</b>\n\n"
            "Qayta urinish uchun /start buyrug'ini yuboring."
        )
    else:
        await callback.answer("❓ Noma'lum holat. Qayta urinib ko'ring.", show_alert=True)
