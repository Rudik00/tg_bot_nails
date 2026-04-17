"""
Запросы к БД для вычисления доступных дней в календаре.

get_user_available_dates  — дни, когда хотя бы один мастер свободен
                            для записи клиента.
get_master_available_dates — дни, когда данный мастер работает
                             (для отображения его расписания).
"""

import calendar as cal_module
from datetime import date

from sqlalchemy import select

from .create_db import SessionLocal
from .models_db import Master, MasterClient


# Должен совпадать со списком в booking_utils.py.
_TIME_SLOTS = ["10:00", "12:00", "14:00", "16:00", "18:00"]
_TOTAL_SLOTS = len(_TIME_SLOTS)


def _parse_work_days(raw: str | None) -> set[int]:
    if not raw:
        return set()
    _MAP = {
        "пн": 0, "вт": 1, "ср": 2,
        "чт": 3, "пт": 4, "сб": 5, "вс": 6,
    }
    return {
        _MAP[c]
        for c in (s.strip().lower() for s in raw.split(","))
        if c in _MAP
    }


def _parse_weekend_days(raw: str | None, month: int) -> set[int]:
    if not raw:
        return set()
    result: set[int] = set()
    for item in raw.split(","):
        candidate = item.strip()
        if "." not in candidate:
            continue
        d_str, m_str = candidate.split(".", maxsplit=1)
        if d_str.isdigit() and m_str.isdigit() and int(m_str) == month:
            result.add(int(d_str))
    return result


async def get_user_available_dates(year: int, month: int) -> set[int]:
    """
    Возвращает числа месяца, когда хотя бы один мастер принимает
    клиентов: работает в этот день недели, не взял выходной и
    у него остался хотя бы один незабронированный временной слот.
    """
    today = date.today()
    _, last_day = cal_module.monthrange(year, month)

    async with SessionLocal() as session:
        masters = (
            await session.execute(select(Master))
        ).scalars().all()

        month_start = date(year, month, 1)
        month_end = date(year, month, last_day)
        booked_rows = (
            await session.execute(
                select(
                    MasterClient.master_id,
                    MasterClient.booking_date,
                    MasterClient.booking_time,
                ).where(
                    MasterClient.booking_date.between(
                        month_start, month_end
                    )
                )
            )
        ).all()

    # { (master_db_id, day_number): count_booked }
    booked_counts: dict[tuple[int, int], int] = {}
    for row in booked_rows:
        key = (row.master_id, row.booking_date.day)
        booked_counts[key] = booked_counts.get(key, 0) + 1

    available_days: set[int] = set()
    for day in range(1, last_day + 1):
        current_date = date(year, month, day)
        if current_date < today:
            continue
        weekday = current_date.weekday()
        for master in masters:
            work_wdays = _parse_work_days(master.work_days)
            if weekday not in work_wdays:
                continue
            wknd = _parse_weekend_days(master.weekend_days, month)
            if day in wknd:
                continue
            booked = booked_counts.get((master.id, day), 0)
            if booked < _TOTAL_SLOTS:
                available_days.add(day)
                break  # достаточно одного доступного мастера

    return available_days


async def get_master_available_dates(
    master_telegram_id: int,
    year: int,
    month: int,
) -> set[int] | None:
    """
    Возвращает числа месяца, когда мастер работает.
    None  — мастер не найден в БД.
    set() — мастер найден, но рабочие дни не настроены.
    """
    today = date.today()
    _, last_day = cal_module.monthrange(year, month)

    async with SessionLocal() as session:
        master = await session.scalar(
            select(Master).where(
                Master.telegram_id == master_telegram_id
            )
        )

    if master is None:
        return None

    work_wdays = _parse_work_days(master.work_days)
    if not work_wdays:
        return set()

    wknd = _parse_weekend_days(master.weekend_days, month)

    available_days: set[int] = set()
    for day in range(1, last_day + 1):
        current_date = date(year, month, day)
        if current_date < today:
            continue
        if (
            current_date.weekday() in work_wdays
            and day not in wknd
        ):
            available_days.add(day)

    return available_days
