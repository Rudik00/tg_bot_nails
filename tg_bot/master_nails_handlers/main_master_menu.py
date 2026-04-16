from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from .states import BookingState
from .add_work_days import records_work_days

router = Router()


# главное меню для мастера
async def master_nails_menu(message: Message, state: FSMContext):
    await state.set_state(BookingState.choosing_menu)
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Добавить рабочие дни", callback_data="menu_1")],
            [InlineKeyboardButton(text="Добавить выходные", callback_data="menu_2")],
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
    # извликаем выбранного пункта меню
    menu_item = callback_query.data.split("_")[1]
    menu_message = callback_query.message

    await callback_query.answer("Ты выбрал пункт меню: " + menu_item)
    await menu_message.delete()

    if menu_item == "1":
        await records_work_days(menu_message, state)

    elif menu_item == "2":
        await menu_message.answer("Ты выбрал: Добавить выходные")

    elif menu_item == "3":
        await menu_message.answer("Ты выбрал: Мои записи")

    elif menu_item == "4":
        await menu_message.answer("Ты выбрал: Мой график")