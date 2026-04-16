from sqlalchemy import select
from .create_db import SessionLocal
from .models_db import Master


async def remove_master_db_handler(id: int) -> str:
    """Удаляет мастера по telegram_id."""
    async with SessionLocal() as session:
        async with session.begin():
            existing_stmt = select(Master).where(
                Master.telegram_id == id
            )
            existing = await session.scalar(existing_stmt)
            if existing is None:
                return "Мастера с таким id нет"

            await session.delete(existing)

        return "Вы удалены из базы данных"
