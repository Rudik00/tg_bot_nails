from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram import Router

from .states import BookingState
from ..database.add_master_db import add_master_db as add_master_db_record


router = Router()


async def add_master_handler(message: Message, state: FSMContext):
    await state.set_state(BookingState.adding_master)
    await message.answer("Введите имя мастера:")


# отлов ввода имени мастера
@router.message(BookingState.adding_master)
async def process_master_name(message: Message, state: FSMContext):
    master_name = message.text
    text = await add_master_db_record(
        master_id=message.from_user.id,
        name=master_name,
    )
    await message.answer(text)
    await state.clear()
