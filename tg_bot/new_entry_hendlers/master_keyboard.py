from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def create_master_keyboard() -> InlineKeyboardMarkup:
    # Список мастеров (пока статичный, позже можно брать из БД).
    masters = ["Анна", "Мария", "София"]
    keyboard = [
        [InlineKeyboardButton(text=master, callback_data=f"master:{master}")]
        for master in masters
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
