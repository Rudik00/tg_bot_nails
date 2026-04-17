from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy import select

from ..database.create_db import SessionLocal
from ..database.models_db import Service


def _format_service_button_text(service: Service) -> str:
    parts = [service.name]
    if service.price is not None:
        parts.append(f"{service.price}.")
    if service.time_services is not None:
        parts.append(f"{service.time_services} мин")
    return " | ".join(parts)


async def get_services() -> list[Service]:
    async with SessionLocal() as session:
        result = await session.execute(select(Service).order_by(Service.id))
        return list(result.scalars().all())


async def get_service_by_id(service_id: int) -> Service | None:
    async with SessionLocal() as session:
        return await session.scalar(
            select(Service).where(Service.id == service_id)
        )


async def choice_service() -> InlineKeyboardMarkup | None:
    services = await get_services()
    if not services:
        return None

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=_format_service_button_text(service),
                    callback_data=f"service:{service.id}",
                )
            ]
            for service in services
        ]
    )
    return keyboard
