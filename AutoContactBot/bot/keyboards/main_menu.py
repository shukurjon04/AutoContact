from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📢 Kanallar")],
            [KeyboardButton(text="👤 Profilim"), KeyboardButton(text="📊 To'lovlar tarixi")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Menyudan tanlang...",
    )
