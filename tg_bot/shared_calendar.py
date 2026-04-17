"""
Единый строитель inline-клавиатуры календаря.

build_user_calendar_keyboard  — кликабельный календарь для клиента,
                                даты передаются из БД.
build_master_schedule_keyboard — отображаемый (некликабельный) календарь
                                 для мастера с навигацией вперёд/назад.
"""

import calendar
from datetime import date

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


WEEKDAY_LABELS = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
MAX_MONTHS_AHEAD = 3


def shift_month(year: int, month: int, delta: int) -> tuple[int, int]:
    month += delta
    if month < 1:
        return year - 1, 12
    if month > 12:
        return year + 1, 1
    return year, month


def _max_month_date(today: date) -> date:
    max_year, max_month = shift_month(
        today.year, today.month, MAX_MONTHS_AHEAD
    )
    return date(max_year, max_month, 1)


def build_user_calendar_keyboard(
    year: int,
    month: int,
    available_days: set[int],
) -> InlineKeyboardMarkup:
    """
    Кликабельный календарь для клиентской записи.
    available_days — числа месяца с доступными слотами.
    Навигация ограничена: сегодня .. сегодня + MAX_MONTHS_AHEAD.
    """
    today = date.today()
    current = date(today.year, today.month, 1)
    displayed = date(year, month, 1)
    max_date = _max_month_date(today)

    show_prev = displayed > current
    show_next = displayed < max_date

    month_title = f"{calendar.month_name[month]} {year}"
    keyboard: list[list[InlineKeyboardButton]] = [
        [
            InlineKeyboardButton(
                text="<" if show_prev else " ",
                callback_data=(
                    f"cal:prev:{year}:{month}"
                    if show_prev
                    else "cal:ignore"
                ),
            ),
            InlineKeyboardButton(
                text=month_title, callback_data="cal:ignore"
            ),
            InlineKeyboardButton(
                text=">" if show_next else " ",
                callback_data=(
                    f"cal:next:{year}:{month}"
                    if show_next
                    else "cal:ignore"
                ),
            ),
        ],
        [
            InlineKeyboardButton(text=lb, callback_data="cal:ignore")
            for lb in WEEKDAY_LABELS
        ],
    ]

    cal = calendar.Calendar(firstweekday=0)
    for week in cal.monthdayscalendar(year, month):
        row: list[InlineKeyboardButton] = []
        for day in week:
            if day == 0 or day not in available_days:
                row.append(
                    InlineKeyboardButton(
                        text=" ", callback_data="cal:ignore"
                    )
                )
            else:
                row.append(
                    InlineKeyboardButton(
                        text=str(day),
                        callback_data=f"cal:day:{year}:{month}:{day}",
                    )
                )
        keyboard.append(row)

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def build_master_schedule_keyboard(
    year: int,
    month: int,
    available_days: set[int],
    master_telegram_id: int,
) -> InlineKeyboardMarkup:
    """
    Некликабельный календарь-расписание для мастера с навигацией.
    Рабочие дни показываются числом, остальные — пустой ячейкой.
    """
    today = date.today()
    current = date(today.year, today.month, 1)
    displayed = date(year, month, 1)
    max_date = _max_month_date(today)

    show_prev = displayed > current
    show_next = displayed < max_date

    mid = master_telegram_id
    month_title = f"{calendar.month_name[month]} {year}"
    keyboard: list[list[InlineKeyboardButton]] = [
        [
            InlineKeyboardButton(
                text="<" if show_prev else " ",
                callback_data=(
                    f"sched:prev:{mid}:{year}:{month}"
                    if show_prev
                    else "sched:ignore"
                ),
            ),
            InlineKeyboardButton(
                text=month_title, callback_data="sched:ignore"
            ),
            InlineKeyboardButton(
                text=">" if show_next else " ",
                callback_data=(
                    f"sched:next:{mid}:{year}:{month}"
                    if show_next
                    else "sched:ignore"
                ),
            ),
        ],
        [
            InlineKeyboardButton(text=lb, callback_data="sched:ignore")
            for lb in WEEKDAY_LABELS
        ],
    ]

    cal = calendar.Calendar(firstweekday=0)
    for week in cal.monthdayscalendar(year, month):
        row: list[InlineKeyboardButton] = []
        for day in week:
            if day == 0 or day not in available_days:
                row.append(
                    InlineKeyboardButton(
                        text=" ", callback_data="sched:ignore"
                    )
                )
            else:
                row.append(
                    InlineKeyboardButton(
                        text=str(day), callback_data="sched:ignore"
                    )
                )
        keyboard.append(row)

    return InlineKeyboardMarkup(inline_keyboard=keyboard)
