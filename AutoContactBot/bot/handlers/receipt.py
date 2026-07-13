"""
Receipt upload handler.
"""
import logging
from io import BytesIO

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from bot.states.payment_states import PaymentState

from bot.services.payment_service import create_pending_transaction
from bot.services.user_service import get_user_by_telegram_id

logger = logging.getLogger(__name__)
router = Router(name="receipt")


@router.message(PaymentState.waiting_for_receipt, F.photo)
async def process_receipt_photo(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    tariff_id = data.get("tariff_id")
    channel_id = data.get("channel_id")

    if not tariff_id or not channel_id:
        await message.answer("❌ Xatolik yuz berdi. Iltimos, boshqatdan boshlang: /start")
        await state.clear()
        return

    user = await get_user_by_telegram_id(message.from_user.id)
    if not user:
        await message.answer("❌ Foydalanuvchi topilmadi.")
        return

    photo = message.photo[-1]
    
    # Yuklab olish
    file_io = BytesIO()
    await message.bot.download(photo.file_id, destination=file_io)
    
    file_name = f"receipt_{message.from_user.id}_{message.message_id}.jpg"
    
    try:
        await create_pending_transaction(
            user=user,
            tariff_id=tariff_id,
            channel_id=channel_id,
            receipt_file_content=file_io.getvalue(),
            file_name=file_name
        )
    except Exception as e:
        logger.exception("Error saving receipt")
        await message.answer("❌ Chekni saqlashda xatolik yuz berdi. Iltimos, keyinroq qayta urinib ko'ring.")
        return

    await state.clear()
    await message.answer(
        "✅ <b>Chek qabul qilindi!</b>\n\n"
        "To'lovingiz adminga yuborildi. Tasdiqlangandan so'ng sizga xabar beramiz va kanalga qo'shamiz."
    )


@router.message(PaymentState.waiting_for_receipt)
async def process_receipt_invalid(message: Message) -> None:
    await message.answer("Iltimos, to'lov chekini <b>rasm (photo)</b> ko'rinishida yuboring.")
