import os

from dotenv import load_dotenv
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from .models_db import Base, Service


load_dotenv()
RAW_DATABASE_URL = os.getenv("DATABASE_URL")

if not RAW_DATABASE_URL:
    raise ValueError("DATABASE_URL не найден в .env")


def _to_async_database_url(database_url: str) -> str:
    # Для create_async_engine нужен драйвер asyncpg.
    if database_url.startswith("postgresql+asyncpg://"):
        return database_url
    if database_url.startswith("postgresql://"):
        return database_url.replace(
            "postgresql://",
            "postgresql+asyncpg://",
            1,
        )
    if database_url.startswith("postgres://"):
        return database_url.replace("postgres://", "postgresql+asyncpg://", 1)
    return database_url


DATABASE_URL = _to_async_database_url(RAW_DATABASE_URL)


# NullPool предотвращает повторное использование соединений asyncpg
# в разных циклах событий
# в задачах рабочих процессов Celery.
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    poolclass=NullPool,
)
SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# Стартовый список услуг
_DEFAULT_SERVICES = [
    Service(id=1, name="Гелевая коррекция", price=30, time_services=150),
    Service(id=2, name="Маникюр + наращивание", price=40, time_services=240),
    Service(id=3, name="Маникюр + покрытие лаком", price=20, time_services=60),
    Service(id=4, name="Маникюр + гель лак", price=30, time_services=150),
]


async def _apply_schema_updates() -> None:
    async with engine.begin() as conn:
        await conn.exec_driver_sql(
            "ALTER TABLE masters "
            "ADD COLUMN IF NOT EXISTS username VARCHAR"
        )
        await conn.exec_driver_sql(
            "ALTER TABLE clients "
            "ADD COLUMN IF NOT EXISTS client_username VARCHAR"
        )
        await conn.exec_driver_sql(
            "ALTER TABLE clients "
            "ADD COLUMN IF NOT EXISTS master_username VARCHAR"
        )


async def init_db() -> None:
    # Создаёт только таблицы, если их ещё нет.
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await _apply_schema_updates()


async def seed_services() -> None:
    # Добавляет стартовые услуги, если таблица services пустая.
    async with SessionLocal() as session:
        result = await session.execute(select(Service))
        if result.scalars().first() is not None:
            return  # услуги уже есть — пропускаем
        session.add_all(_DEFAULT_SERVICES)
        await session.commit()
