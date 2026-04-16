from .create_db import SessionLocal
from sqlalchemy import select

from .models_db import Master


async def add_week_days_db_handler(
    master_id: int,
    week_days: list[str] | str,
) -> bool:
    # Добавляет выходные дни мастера.
    if isinstance(week_days, list):
        normalized_days = [day.strip() for day in week_days if day.strip()]
        serialized_week_days = ",".join(normalized_days)
    else:
        serialized_week_days = week_days.strip()

    async with SessionLocal() as session:
        async with session.begin():
            existing_stmt = select(Master).where(
                Master.telegram_id == master_id
            )
            existing = await session.scalar(existing_stmt)
            if existing is None:
                return False

            existing.weekend_days = serialized_week_days
            session.add(existing)

        return True
