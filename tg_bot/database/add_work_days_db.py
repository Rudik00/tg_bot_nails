from .create_db import SessionLocal
from sqlalchemy import select

from .models_db import Master


async def add_work_days_db_handler(
    master_id: int,
    work_days: list[str] | str,
) -> bool:
    """Добавляет рабочие дни мастера."""
    if isinstance(work_days, list):
        normalized_days = [
            day.strip().lower() for day in work_days if day.strip()
        ]
        serialized_work_days = ",".join(normalized_days)
    else:
        serialized_work_days = work_days.strip().lower()

    async with SessionLocal() as session:
        async with session.begin():
            existing_stmt = select(Master).where(
                Master.telegram_id == master_id
            )
            existing = await session.scalar(existing_stmt)
            if existing is None:
                return False

            existing.work_days = serialized_work_days
            session.add(existing)

        return True
