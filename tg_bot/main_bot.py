import os
import asyncio

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    WebAppInfo,
)
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup


dp = Dispatcher(storage=MemoryStorage())


class AddProductState(StatesGroup):
    waiting_url = State()
    waiting_url_or_id = State()
    waiting_delete_url_or_id = State()


def get_token() -> str:
    load_dotenv()  # читает .env
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN не найден в .env")
    return token


async def main_tg_bot(token: str):
    bot = Bot(token=token)
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


@dp.message(Command("start"))
async def start_handler(message: Message):
    await message.answer(
        "Тебя приветсвует бот для записи на ноготочки! 💅\n"
        )


@dp.message(Command("info"))
async def info_handler(message: Message):
    await message.answer(
        "Я бот для записи на ноготочки! 💅\n"
        "Я помогу тебе записаться на маникюр и следить за твоими записями.\n"
        "Больше функций скоро! 💪"
    )
#                         добавление товара по ссылке
# ________________________________________________________________________________________

# при вызове команды /new_entry
# бот отправляет инлайн кнопки с услугами по моникюру
# ловит ответ пользователя и отправляет пользователю календарь с датами для записи на маникюр
# после выбора даты отправляет пользователю время для записи на маникюр
# после выбора времени показывает какие мастера свободны в это время и предлагает выбрать мастера


@dp.message(Command("new_entry"))
async def new_entry_handler(message: Message, state: FSMContext):
    await message.answer("Выбери услугу которая тебе нужна")


if __name__ == "__main__":
    token = get_token()
    asyncio.run(main_tg_bot(token))
