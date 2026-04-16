from .create_db import SessionLocal
from sqlalchemy import select

from .models_db import Master


async def add_master_db(master_id: int, name: str) -> str:
    """Добавляет мастера, если мастера с таким telegram_id еще нет."""
    async with SessionLocal() as session:
        async with session.begin():
            existing_stmt = select(Master).where(
                Master.telegram_id == master_id
            )
            existing = await session.scalar(existing_stmt)
            if existing is not None:
                return "Мастер с таким id уже есть"

            master = Master(
                telegram_id=master_id,
                name=name,
            )
            session.add(master)

        return "Вы добавлены в базу данных"
