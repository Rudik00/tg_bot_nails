from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ..database.create_db import SessionLocal
from ..database.models_db import Client, Service
from ..telegram_contact import build_contact_link_html, escape_html_text


# Здесь береться информация о записи клиента из БД
# и формируется сообщение для клиента с его записями
async def show_entries_clients_db(client_telegram_id: int) -> str:
    now = datetime.now()

    async with SessionLocal() as session:
        result = await session.execute(
            select(Client)
            .options(selectinload(Client.service))
            .where(Client.client_telegram_id == client_telegram_id)
            .order_by(Client.booking_date, Client.booking_time)
        )
        bookings = result.scalars().all()

    actual_bookings = [
        booking
        for booking in bookings
        if datetime.combine(
            booking.booking_date,
            booking.booking_time,
        ) > now
    ]
    if not actual_bookings:
        return "У вас нет будущих записей."

    entries_info = []
    for entry in actual_bookings:
        service: Service | None = entry.service
        service_name = service.name if service is not None else "-"
        master_contact = build_contact_link_html(
            entry.master_username,
            entry.master_telegram_id,
            entry.master_name,
        )
        entries_info.append(
            f"<b>Дата:</b> {entry.booking_date.strftime('%d.%m.%Y')}\n"
            f"<b>Время:</b> {entry.booking_time.strftime('%H:%M')}\n"
            f"<b>Услуга:</b> {escape_html_text(service_name)}\n"
            f"<b>Мастер:</b> {escape_html_text(entry.master_name)}\n"
            f"<b>Ссылка для связи:</b> {master_contact}"
        )

    return "<b>Ваши записи:</b>\n\n" + "\n\n".join(entries_info)
