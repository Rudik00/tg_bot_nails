from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from ..database.list_entries_db import show_entries_clients_db

router = Router()


async def show_entries_clients(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        await show_entries_clients_db(message.from_user.id),
        parse_mode="HTML",
    )
