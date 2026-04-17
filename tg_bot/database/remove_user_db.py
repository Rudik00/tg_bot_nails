from datetime import datetime

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from .create_db import SessionLocal
from .models_db import Client, Master, MasterClient


async def get_user_cancellable_bookings(
    client_telegram_id: int,
) -> list[Client]:
    now = datetime.now()

    async with SessionLocal() as session:
        result = await session.execute(
            select(Client)
            .options(selectinload(Client.service))
            .where(Client.client_telegram_id == client_telegram_id)
            .order_by(Client.booking_date, Client.booking_time)
        )
        bookings = result.scalars().all()

    return [
        booking
        for booking in bookings
        if datetime.combine(
            booking.booking_date,
            booking.booking_time,
        ) > now
    ]


def build_user_cancellation_keyboard(
    bookings: list[Client],
) -> InlineKeyboardMarkup:
    keyboard = []
    for booking in bookings:
        service_name = (
            booking.service.name if booking.service else str(booking.id)
        )
        button_text = (
            f"{booking.booking_date.strftime('%d.%m.%Y')} | "
            f"{booking.booking_time.strftime('%H:%M')} | "
            f"{service_name}"
        )
        keyboard.append(
            [
                InlineKeyboardButton(
                    text=button_text,
                    callback_data=f"ucancel:select:{booking.id}",
                )
            ]
        )

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


async def get_user_booking_details(
    client_telegram_id: int,
    booking_id: int,
) -> Client | None:
    async with SessionLocal() as session:
        return await session.scalar(
            select(Client)
            .options(selectinload(Client.service))
            .where(
                Client.id == booking_id,
                Client.client_telegram_id == client_telegram_id,
            )
        )


async def cancel_user_booking(
    client_telegram_id: int,
    booking_id: int,
) -> bool:
    async with SessionLocal() as session:
        async with session.begin():
            booking = await session.scalar(
                select(Client).where(
                    Client.id == booking_id,
                    Client.client_telegram_id == client_telegram_id,
                )
            )
            if booking is None:
                return False

            master = await session.scalar(
                select(Master).where(
                    Master.telegram_id == booking.master_telegram_id
                )
            )
            if master is not None:
                result = await session.execute(
                    select(MasterClient).where(
                        MasterClient.master_id == master.id,
                        MasterClient.booking_date == booking.booking_date,
                        MasterClient.booking_time == booking.booking_time,
                        MasterClient.client_telegram_id == client_telegram_id,
                    )
                )
                for master_booking in result.scalars().all():
                    await session.delete(master_booking)

            await session.delete(booking)

    return True
