from datetime import date, datetime

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy import select

from ..database.availability_db import _parse_weekend_days, _parse_work_days
from ..database.create_db import SessionLocal
from ..database.models_db import Master, MasterClient


async def get_master_by_telegram_id(
    master_telegram_id: int,
) -> Master | None:
    async with SessionLocal() as session:
        return await session.scalar(
            select(Master).where(Master.telegram_id == master_telegram_id)
        )


async def get_available_masters(
    selected_date: date,
    selected_time: str,
) -> list[Master]:
    booking_time = datetime.strptime(selected_time, "%H:%M").time()

    async with SessionLocal() as session:
        masters = (
            await session.execute(select(Master).order_by(Master.name))
        ).scalars().all()
        booked_master_ids = set(
            (
                await session.execute(
                    select(MasterClient.master_id).where(
                        MasterClient.booking_date == selected_date,
                        MasterClient.booking_time == booking_time,
                    )
                )
            ).scalars().all()
        )

    weekday = selected_date.weekday()
    day = selected_date.day
    available_masters: list[Master] = []

    for master in masters:
        work_days = _parse_work_days(master.work_days)
        if weekday not in work_days:
            continue

        weekend_days = _parse_weekend_days(
            master.weekend_days,
            selected_date.month,
        )
        if day in weekend_days:
            continue

        if master.id in booked_master_ids:
            continue

        available_masters.append(master)

    return available_masters


async def create_master_keyboard(
    selected_date: date,
    selected_time: str,
) -> InlineKeyboardMarkup | None:
    masters = await get_available_masters(selected_date, selected_time)
    if not masters:
        return None

    keyboard = [
        [
            InlineKeyboardButton(
                text=master.name,
                callback_data=f"master:{master.telegram_id}",
            )
        ]
        for master in masters
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
