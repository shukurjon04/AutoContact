"""
Profile menu — shows active subscriptions and payment history.
"""
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from bot.services.subscription_service import get_user_active_subscriptions
from bot.services.payment_service import get_user_transaction_history

logger = logging.getLogger(__name__)
router = Router(name="profile")


@router.message(F.text == "👤 Profilim")
async def show_profile(message: Message) -> None:
    telegram_id = message.from_user.id
    subscriptions = await get_user_active_subscriptions(telegram_id)

    if not subscriptions:
        text = (
            "👤 <b>Profilingiz</b>\n\n"
            "Sizda hozircha faol obunalar yo'q.\n\n"
            "📢 Kanallarga obuna bo'lish uchun <b>Kanallar</b> bo'limiga o'ting."
        )
    else:
        lines = ["👤 <b>Faol obunalaringiz:</b>\n"]
        for sub in subscriptions:
            lines.append(
                f"📢 <b>{sub.channel.name}</b>\n"
                f"   📅 Tugash sanasi: {sub.end_date.strftime('%d.%m.%Y')}\n"
                f"   ⏳ Qoldi: {sub.remaining_days} kun\n"
            )
        text = "\n".join(lines)

    await message.answer(text)


@router.message(F.text == "📊 To'lovlar tarixi")
async def show_payment_history(message: Message) -> None:
    telegram_id = message.from_user.id
    transactions = await get_user_transaction_history(telegram_id, limit=20)

    if not transactions:
        await message.answer("📊 Sizda hozircha to'lovlar tarixi yo'q.")
        return

    lines = ["📊 <b>So'nggi to'lovlaringiz:</b>\n"]
    for tx in transactions:
        status_emoji = {"paid": "✅", "pending": "⏳", "cancelled": "❌", "failed": "❌"}.get(
            tx.status, "❓"
        )
        lines.append(
            f"{status_emoji} <b>{tx.channel.name}</b> — {tx.amount_uzs:,} UZS\n"
            f"   📅 {tx.created_at.strftime('%d.%m.%Y %H:%M')}\n"
        )

    await message.answer("\n".join(lines))
