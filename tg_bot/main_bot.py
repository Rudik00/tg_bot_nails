import os
import asyncio

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

# ROUTERS
from .new_entry_hendlers.booking_handlers import (
    router as booking_router,
)
from .users_handlers.order_cancellation import (
    router as order_cancellation_router,
)
from .master_nails_handlers.main_master_menu import (
    router as master_menu_router,
)
from .master_nails_handlers.add_work_days import (
    router as add_work_days_router,
)
from .master_nails_handlers.add_master import (
    router as add_master_router,
)
from .master_nails_handlers.remove_master import (
    router as remove_master_router,
)
from .master_nails_handlers.add_week_days import (
    router as add_week_days_router,
)
from .master_nails_handlers.my_schedule import (
    router as my_schedule_router,
)
from .master_nails_handlers.list_clients import (
    router as list_clients_router,
)

from .basic_handlers import info_handler as show_info
from .basic_handlers import start_handler as show_start
from .new_entry_hendlers.booking_handlers import (
    new_entry_handler as start_new_entry,
)
from .users_handlers.list_entries import show_entries_clients
from .users_handlers.order_cancellation import cancel_user_registration
from .master_nails_handlers.main_master_menu import master_nails_menu

from .database.create_db import init_db, seed_services
from .master_nails_handlers.add_master import add_master_handler
from .master_nails_handlers.remove_master import remove_master_handler


dp = Dispatcher(storage=MemoryStorage())


# Команда для начала общения с ботом
@dp.message(Command("start"))
async def start_command(message: Message):
    await show_start(message)


#                                     Общие команды для всех пользователей
# Команда для получения информации о боте
@dp.message(Command("info"))
async def info_command(message: Message):
    await show_info(message)


# команда для начала новой записи
@dp.message(Command("new_entry"))
async def new_entry_command(message: Message, state: FSMContext):
    await start_new_entry(message, state)


# команда для отображения списка записей клиента
@dp.message(Command("list_of_entries"))
async def list_of_entries_command(message: Message, state: FSMContext):
    await show_entries_clients(message, state)


# команда для отмены записи клиента
@dp.message(Command("cancellation"))
async def cancellation_command(message: Message, state: FSMContext):
    await cancel_user_registration(message, state)


#                                     Главное меню для мастера
# информация для мастеров (графики и записи)
@dp.message(Command("master_info"))
async def master_info_command(message: Message, state: FSMContext):
    await master_nails_menu(message, state)


# добавление мастера в таблицу
@dp.message(Command("add_m"))
async def add_master_command(message: Message, state: FSMContext):
    await add_master_handler(message, state)


# удаление мастера из таблицы
@dp.message(Command("rem_m"))
async def remove_master_command(message: Message, state: FSMContext):
    await remove_master_handler(message, state)


def get_token() -> str:
    load_dotenv()  # читает .env
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN не найден в .env")
    return token


async def main_tg_bot(token: str):
    # Инициализируем БД и заполняем услуги при первом запуске
    await init_db()
    await seed_services()

    # Запускаем polling и гарантированно закрываем сессию бота.
    bot = Bot(token=token)
    dp.include_router(booking_router)
    dp.include_router(master_menu_router)
    dp.include_router(add_work_days_router)
    dp.include_router(add_master_router)
    dp.include_router(remove_master_router)
    dp.include_router(add_week_days_router)
    dp.include_router(my_schedule_router)
    dp.include_router(list_clients_router)
    dp.include_router(order_cancellation_router)
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    token = get_token()
    asyncio.run(main_tg_bot(token))
