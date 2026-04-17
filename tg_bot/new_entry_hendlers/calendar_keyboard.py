from aiogram.types import InlineKeyboardMarkup

from ..database.availability_db import get_user_available_dates
from ..shared_calendar import build_user_calendar_keyboard


async def create_calendar_keyboard(
    year: int, month: int
) -> InlineKeyboardMarkup:
    # Использует БД для определения доступных дат всех мастеров.
    available_days = await get_user_available_dates(year, month)
    return build_user_calendar_keyboard(year, month, available_days)
