"""Async wrappers around TelegramUser ORM operations."""
from asgiref.sync import sync_to_async
from apps.users.models import TelegramUser


@sync_to_async
def get_or_create_user(
    telegram_id: int,
    first_name: str,
    last_name: str,
    username: str | None,
    language_code: str,
) -> tuple[TelegramUser, bool]:
    user, created = TelegramUser.objects.get_or_create(
        telegram_id=telegram_id,
        defaults={
            "first_name": first_name,
            "last_name": last_name or "",
            "username": username,
            "language_code": language_code,
        },
    )
    if not created:
        user.update_from_telegram(
            first_name=first_name,
            last_name=last_name or "",
            username=username,
            language_code=language_code,
        )
    return user, created


@sync_to_async
def get_user_by_telegram_id(telegram_id: int) -> TelegramUser | None:
    return TelegramUser.objects.filter(telegram_id=telegram_id).first()
