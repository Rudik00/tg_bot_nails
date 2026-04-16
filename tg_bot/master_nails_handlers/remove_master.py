from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram import Router
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from .states import BookingState
from ..database.remove_master_db import remove_master_db_handler

router = Router()


async def remove_master_handler(message: Message, state: FSMContext):
    # инлайн клавиши для подтверждения удаления
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Да", callback_data="confirm_remove")],
            [InlineKeyboardButton(text="Нет", callback_data="cancel_remove")],
        ]
    )
    await state.set_state(BookingState.removing_master)
    await message.answer("Вы уверены, что хотите удалить себя из числа мастеров?", reply_markup=keyboard)


# отлов подтверждения удаления
@router.callback_query(lambda c: c.data in ["confirm_remove", "cancel_remove"])
async def process_remove_confirmation(
        callback_query: CallbackQuery,
        state: FSMContext
        ):
    if callback_query.data == "confirm_remove":
        await remove_master_db_handler(callback_query.from_user.id)
        await callback_query.message.answer("Вы были удалены из числа мастеров.")
    else:
        await callback_query.message.answer("Удаление отменено.")

    message = callback_query.message
    await message.delete()
    await state.clear()
