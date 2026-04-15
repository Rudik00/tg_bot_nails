import os
import asyncio

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from .basic_handlers import info_handler as show_info
from .basic_handlers import start_handler as show_start
from .booking_handlers import new_entry_handler as start_new_entry
from .booking_handlers import router as booking_router


dp = Dispatcher(storage=MemoryStorage())


@dp.message(Command("start"))
async def start_command(message: Message):
    await show_start(message)


@dp.message(Command("info"))
async def info_command(message: Message):
    await show_info(message)


@dp.message(Command("new_entry"))
async def new_entry_command(message: Message, state: FSMContext):
    await start_new_entry(message, state)


def get_token() -> str:
    load_dotenv()  # читает .env
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN не найден в .env")
    return token


async def main_tg_bot(token: str):
    # Запускаем polling и гарантированно закрываем сессию бота.
    bot = Bot(token=token)
    dp.include_router(booking_router)
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    token = get_token()
    asyncio.run(main_tg_bot(token))
