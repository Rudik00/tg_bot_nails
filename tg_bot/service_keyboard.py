from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def choice_service():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Услуга 1", callback_data="service_1")],
            [InlineKeyboardButton(text="Услуга 2", callback_data="service_2")],
            [InlineKeyboardButton(text="Услуга 3", callback_data="service_3")],
        ]
    )
    return keyboard
