import calendar
from datetime import date

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from .booking_utils import get_available_time_slots


WEEKDAY_LABELS = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]


def create_calendar_keyboard(year: int, month: int) -> InlineKeyboardMarkup:
    # Рисует календарь: доступные даты цифрами, недоступные — пустые клетки.
    today = date.today()
    month_title = f"{calendar.month_name[month]} {year}"
    current_month = date(today.year, today.month, 1)
    displayed_month = date(year, month, 1)
    show_prev_button = displayed_month > current_month

    keyboard: list[list[InlineKeyboardButton]] = [
        [
            InlineKeyboardButton(
                text="<" if show_prev_button else " ",
                callback_data=(
                    f"cal:prev:{year}:{month}"
                    if show_prev_button
                    else "cal:ignore"
                ),
            ),
            InlineKeyboardButton(text=month_title, callback_data="cal:ignore"),
            InlineKeyboardButton(
                text=">", callback_data=f"cal:next:{year}:{month}"
            ),
        ],
        [
            InlineKeyboardButton(text=day_name, callback_data="cal:ignore")
            for day_name in WEEKDAY_LABELS
        ],
    ]

    # Формируем сетку недель выбранного месяца.
    cal = calendar.Calendar(firstweekday=0)
    for week in cal.monthdayscalendar(year, month):
        row: list[InlineKeyboardButton] = []
        for day in week:
            if day == 0:
                row.append(
                    InlineKeyboardButton(text=" ", callback_data="cal:ignore")
                )
            else:
                current_date = date(year, month, day)
                # Дата доступна, если не в прошлом и есть доступные слоты.
                is_available_date = (
                    current_date >= today
                    and bool(get_available_time_slots(current_date))
                )

                if not is_available_date:
                    row.append(
                        InlineKeyboardButton(
                            text=" ", callback_data="cal:ignore"
                        )
                    )
                    continue

                row.append(
                    InlineKeyboardButton(
                        text=str(day),
                        callback_data=f"cal:day:{year}:{month}:{day}",
                    )
                )
        keyboard.append(row)
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
