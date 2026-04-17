from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from .states import BookingState
from .add_work_days import records_work_days
from .add_week_days import records_week_days
from .list_clients import show_master_clients
from .my_schedule import show_master_schedule
from ..database.add_master_db import sync_master_username
from ..database.user_verification import verification_master

router = Router()


# главное меню для мастера
async def master_nails_menu(message: Message, state: FSMContext):
    if await verification_master(message.from_user.id):
        await sync_master_username(
            message.from_user.id,
            message.from_user.username,
        )

    await state.set_state(BookingState.choosing_menu)
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Добавить рабочие дни",
                    callback_data="menu_1",
                )
            ],
            [
                InlineKeyboardButton(
                    text="Добавить выходные",
                    callback_data="menu_2",
                )
            ],
            [InlineKeyboardButton(text="Мои записи", callback_data="menu_3")],
            [InlineKeyboardButton(text="Мой график", callback_data="menu_4")],
        ]
    )
    await message.answer(
        "Выбери что хочешь сделать:", reply_markup=keyboard
    )


# отлов выбора пункта меню
@router.callback_query(lambda c: c.data.startswith("menu_"))
async def menu_callback_handler(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    # извлекаем выбранного пункта меню
    menu_item = callback_query.data.split("_")[1]
    await callback_query.message.delete()
    message = callback_query.message

    if menu_item == "1":
        await records_work_days(
            message,
            state,
            callback_query.from_user.id,
        )

    elif menu_item == "2":
        await records_week_days(
            message,
            state,
            callback_query.from_user.id,
        )

    elif menu_item == "3":
        await show_master_clients(
            message,
            callback_query.from_user.id,
        )

    elif menu_item == "4":
        await show_master_schedule(
            message,
            state,
            callback_query.from_user.id,
        )

    await callback_query.answer()
