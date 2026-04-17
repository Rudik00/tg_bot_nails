from .create_db import SessionLocal
from sqlalchemy import select

from .models_db import Master


async def add_master_db(
    master_id: int,
    name: str,
    username: str | None = None,
) -> str:
    """Добавляет мастера, если мастера с таким telegram_id еще нет."""
    async with SessionLocal() as session:
        async with session.begin():
            existing_master = await session.scalar(
                select(Master).where(Master.telegram_id == master_id)
            )
            if existing_master is not None:
                return "Вы уже добавлены в базу данных"

            master = Master(
                telegram_id=master_id,
                username=username,
                name=name,
            )
            session.add(master)

        return "Вы добавлены в базу данных"


async def sync_master_username(
    master_id: int,
    username: str | None,
) -> None:
    async with SessionLocal() as session:
        async with session.begin():
            master = await session.scalar(
                select(Master).where(Master.telegram_id == master_id)
            )
            if master is None:
                return
            master.username = username
