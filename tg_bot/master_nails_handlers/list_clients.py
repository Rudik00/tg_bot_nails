from datetime import datetime

from aiogram import Router
from aiogram.types import CallbackQuery, InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup, Message
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ..database.create_db import SessionLocal
from ..database.models_db import Client, Service
from ..telegram_contact import build_contact_link_html, escape_html_text


router = Router()


def _build_refresh_keyboard(
    master_telegram_id: int,
) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Обновить записи",
                    callback_data=f"clients:refresh:{master_telegram_id}",
                )
            ]
        ]
    )


def _build_booking_messages(bookings: list[Client]) -> list[str]:
    chunks: list[str] = []
    current_chunk = ["<b>Мои записи</b>"]
    current_day: str | None = None

    for booking in bookings:
        service: Service | None = booking.service
        service_name = service.name if service is not None else "-"
        price_text = (
            str(service.price)
            if service is not None and service.price is not None
            else "-"
        )
        duration_text = (
            f"{service.time_services} мин"
            if service is not None and service.time_services is not None
            else "-"
        )
        client_contact = build_contact_link_html(
            booking.client_username,
            booking.client_telegram_id,
            "Связаться с клиентом",
        )
        booking_day = booking.booking_date.strftime("%d.%m.%Y")

        block_parts: list[str] = []
        if booking_day != current_day:
            current_day = booking_day
            block_parts.append(f"\n\n<b>{booking_day}</b>")

        block_parts.append(
            "\n"
            f"<b>Время:</b> {booking.booking_time.strftime('%H:%M')}\n"
            f"<b>Услуга:</b> {escape_html_text(service_name)}\n"
            f"<b>Стоимость:</b> {escape_html_text(price_text)}\n"
            f"<b>Длительность:</b> {escape_html_text(duration_text)}\n"
            f"<b>Клиент:</b> {client_contact}\n"
            "<b>--------------------</b>"
        )
        booking_block = "".join(block_parts)

        next_len = len("".join(current_chunk)) + len(booking_block)
        if next_len > 3500:
            chunks.append("".join(current_chunk))
            current_chunk = ["<b>Мои записи</b>"]
            if booking_day != current_day:
                current_chunk.append(f"\n\n<b>{booking_day}</b>")
                current_day = booking_day
            else:
                current_chunk.append(f"\n\n<b>{booking_day}</b>")
            current_chunk.append(
                "\n"
                f"<b>Время:</b> {booking.booking_time.strftime('%H:%M')}\n"
                f"<b>Услуга:</b> {escape_html_text(service_name)}\n"
                f"<b>Стоимость:</b> {escape_html_text(price_text)}\n"
                f"<b>Длительность:</b> {escape_html_text(duration_text)}\n"
                f"<b>Клиент:</b> {client_contact}\n"
                "<b>--------------------</b>"
            )
            continue

        current_chunk.append(booking_block)

    if current_chunk:
        chunks.append("".join(current_chunk))

    return chunks


async def show_master_clients(
    message: Message,
    master_telegram_id: int,
) -> None:
    now = datetime.now()

    async with SessionLocal() as session:
        result = await session.execute(
            select(Client)
            .options(selectinload(Client.service))
            .where(Client.master_telegram_id == master_telegram_id)
            .order_by(Client.booking_date, Client.booking_time)
        )
        bookings = result.scalars().all()

    future_bookings = [
        booking
        for booking in bookings
        if datetime.combine(
            booking.booking_date,
            booking.booking_time,
        ) > now
    ]

    if not future_bookings:
        await message.answer(
            "У тебя пока нет будущих записей",
            reply_markup=_build_refresh_keyboard(master_telegram_id),
        )
        return

    chunks = _build_booking_messages(future_bookings)

    last_index = len(chunks) - 1
    for index, chunk in enumerate(chunks):
        reply_markup = None
        if index == last_index:
            reply_markup = _build_refresh_keyboard(master_telegram_id)
        await message.answer(
            chunk,
            parse_mode="HTML",
            reply_markup=reply_markup,
        )


@router.callback_query(lambda c: c.data.startswith("clients:refresh:"))
async def refresh_master_clients_handler(
    callback_query: CallbackQuery,
) -> None:
    master_telegram_id = int(
        callback_query.data.split(":", maxsplit=2)[2]
    )
    await callback_query.message.delete()
    await show_master_clients(
        callback_query.message,
        master_telegram_id,
    )
    await callback_query.answer("Список обновлён")
