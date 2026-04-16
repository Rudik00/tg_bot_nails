from .models_db import Master, Client
from .create_db import SessionLocal
from sqlalchemy import select


async def verification_master(telegram_id: int) -> bool:
    """Проверяет, есть ли мастер с данным telegram_id в базе данных."""
    async with SessionLocal() as session:
        async with session.begin():
            existing_stmt = select(Master).where(
                Master.telegram_id == telegram_id
            )
            existing = await session.scalar(existing_stmt)
            if existing is None:
                return False
            return True


async def verification_client(telegram_id: int) -> bool:
    """Проверяет, есть ли клиент с данным telegram_id в базе данных."""
    async with SessionLocal() as session:
        async with session.begin():
            existing_stmt = select(Client).where(
                Client.telegram_id == telegram_id
            )
            existing = await session.scalar(existing_stmt)
            if existing is None:
                return False
            return True
