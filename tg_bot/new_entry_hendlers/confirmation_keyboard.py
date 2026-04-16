from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def create_confirmation_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text="Всё верно", callback_data="confirm:yes")],
        [InlineKeyboardButton(text="Отмена", callback_data="confirm:cancel")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
