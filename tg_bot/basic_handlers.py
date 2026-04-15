from aiogram.types import Message


async def start_handler(message: Message):
    await message.answer("Тебя приветсвует бот для записи на ноготочки! 💅\n")


async def info_handler(message: Message):
    await message.answer(
        "Я бот для записи на ноготочки! 💅\n"
        "Я помогу тебе записаться на маникюр и следить за твоими записями.\n"
        "Больше функций скоро! 💪"
    )
