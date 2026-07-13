"""
Subscription flow: channel list → tariff select → payment.
"""
import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message

from bot.keyboards.subscription import (
    get_channels_keyboard,
    get_tariffs_keyboard,
)
from bot.services.channel_service import get_active_channels, get_channel_tariffs
from bot.services.user_service import get_user_by_telegram_id
from aiogram.fsm.context import FSMContext
from bot.states.payment_states import PaymentState

logger = logging.getLogger(__name__)
router = Router(name="subscription")


# ---------------------------------------------------------------------------
# Kanal ro'yxatini ko'rsatish
# ---------------------------------------------------------------------------
@router.message(F.text == "📢 Kanallar")
async def show_channels(message: Message) -> None:
    channels = await get_active_channels()
    if not channels:
        await message.answer("😔 Hozircha faol kanallar mavjud emas.")
        return
    await message.answer(
        "📢 <b>Mavjud kanallar:</b>\nQuyidagilardan birini tanlang:",
        reply_markup=get_channels_keyboard(channels),
    )


# ---------------------------------------------------------------------------
# Orqaga — kanallar ro'yxatiga qaytish
# ---------------------------------------------------------------------------
@router.callback_query(F.data == "back:channels")
async def back_to_channels(callback: CallbackQuery) -> None:
    channels = await get_active_channels()
    if not channels:
        await callback.answer("Hozircha faol kanallar yo'q.", show_alert=True)
        return
    await callback.message.edit_text(
        "📢 <b>Mavjud kanallar:</b>\nQuyidagilardan birini tanlang:",
        reply_markup=get_channels_keyboard(channels),
    )
    await callback.answer()


# ---------------------------------------------------------------------------
# Tarif ro'yxatini ko'rsatish
# ---------------------------------------------------------------------------
@router.callback_query(F.data.startswith("channel:"))
async def show_tariffs(callback: CallbackQuery) -> None:
    channel_id = int(callback.data.split(":")[1])
    tariffs = await get_channel_tariffs(channel_id)

    if not tariffs:
        await callback.answer(
            "Bu kanal uchun hozircha tariflar mavjud emas.", show_alert=True
        )
        return

    channel_name = tariffs[0].channel.name
    await callback.message.edit_text(
        f"📋 <b>{channel_name}</b> uchun tariflar:\n\nQuyidagilardan birini tanlang:",
        reply_markup=get_tariffs_keyboard(tariffs, channel_id),
    )
    await callback.answer()


# ---------------------------------------------------------------------------
# To'lov havolasi yaratish
# ---------------------------------------------------------------------------
@router.callback_query(F.data.startswith("tariff:"))
async def process_tariff_selection(callback: CallbackQuery, state: FSMContext) -> None:
    parts = callback.data.split(":")
    tariff_id = int(parts[1])
    channel_id = int(parts[2])

    user = await get_user_by_telegram_id(callback.from_user.id)
    if not user:
        await callback.answer("Avval /start buyrug'ini yuboring.", show_alert=True)
        return

    # Get payment settings from DB instead of hardcode
    from asgiref.sync import sync_to_async
    from apps.core.models import PaymentSettings
    settings_obj = await sync_to_async(PaymentSettings.load)()
    card_number = settings_obj.card_number
    card_owner = settings_obj.card_owner

    await state.update_data(tariff_id=tariff_id, channel_id=channel_id)
    await state.set_state(PaymentState.waiting_for_receipt)

    text = (
        "💳 <b>To'lov qilish</b>\n\n"
        f"Iltimos, to'lovni quyidagi karta raqamiga amalga oshiring:\n\n"
        f"💳 <b>{card_number}</b>\n"
        f"👤 <b>{card_owner}</b>\n\n"
        "To'lovni amalga oshirgach, <b>to'lov cheki rasmini (skrinshot)</b> shu yerga yuboring."
    )

    await callback.message.edit_text(text)
    await callback.answer()
