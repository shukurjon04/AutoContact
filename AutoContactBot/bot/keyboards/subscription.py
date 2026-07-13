from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_channels_keyboard(channels) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for ch in channels:
        builder.button(
            text=f"📢 {ch.name}",
            callback_data=f"channel:{ch.id}",
        )
    builder.adjust(1)
    return builder.as_markup()


def get_tariffs_keyboard(tariffs, channel_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for tariff in tariffs:
        label = f"{tariff.name} — {tariff.final_price:,.0f} UZS"
        if tariff.discount_percent:
            label += f" (-{tariff.discount_percent:.0f}%)"
        builder.button(
            text=label,
            callback_data=f"tariff:{tariff.id}:{channel_id}",
        )
    builder.button(text="⬅️ Orqaga", callback_data="back:channels")
    builder.adjust(1)
    return builder.as_markup()


def get_payment_keyboard(payment_url: str, transaction_id: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="💳 To'lov qilish", url=payment_url)
    builder.button(text="✅ To'lovni tekshirish", callback_data=f"check_payment:{transaction_id}")
    builder.adjust(1)
    return builder.as_markup()
