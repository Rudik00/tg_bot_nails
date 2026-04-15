from datetime import date

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from .booking_utils import get_available_time_slots


def create_time_keyboard(selected_date: date) -> InlineKeyboardMarkup:
    # Показывает только доступное время для конкретной даты.
    slots = get_available_time_slots(selected_date)
    keyboard = [
        [InlineKeyboardButton(text=slot, callback_data=f"time:{slot}")]
        for slot in slots
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
