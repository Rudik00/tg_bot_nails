from datetime import date

from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup, Message  # noqa: F401

from ..database.availability_db import get_master_available_dates
from ..shared_calendar import build_master_schedule_keyboard


router = Router()


async def show_master_schedule(
    message: Message,
    state: FSMContext,
    master_telegram_id: int,
) -> None:
    today = date.today()
    available_days = await get_master_available_dates(
        master_telegram_id, today.year, today.month
    )

    if available_days is None:
        await message.answer("Вы не зарегистрированы как мастер.")
        return

    if not available_days and available_days is not None:
        await message.answer(
            "Сначала укажите рабочие дни через пункт меню "
            "'Добавить рабочие дни'."
        )
        return

    calendar_markup = build_master_schedule_keyboard(
        today.year, today.month, available_days, master_telegram_id
    )

    schedule_msg = await message.answer(
        "Твой график на текущий месяц:",
        reply_markup=calendar_markup,
    )
    close_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Всё?",
                    callback_data=(
                        f"sched:close:{schedule_msg.message_id}"
                    ),
                )
            ]
        ]
    )
    await message.answer("Всё?", reply_markup=close_markup)
    await state.clear()


@router.callback_query(lambda c: c.data == "sched:ignore")
async def schedule_ignore_handler(callback_query: CallbackQuery) -> None:
    await callback_query.answer()


@router.callback_query(
    lambda c: (
        c.data.startswith("sched:prev:")
        or c.data.startswith("sched:next:")
    )
)
async def schedule_nav_handler(callback_query: CallbackQuery) -> None:
    parts = callback_query.data.split(":")
    # sched:prev:{mid}:{year}:{month}  or  sched:next:{mid}:{year}:{month}
    _, direction, mid_str, year_str, month_str = parts
    master_telegram_id = int(mid_str)
    year = int(year_str)
    month = int(month_str)
    delta = -1 if direction == "prev" else 1

    month += delta
    if month < 1:
        year -= 1
        month = 12
    elif month > 12:
        year += 1
        month = 1

    available_days = await get_master_available_dates(
        master_telegram_id, year, month
    )
    if available_days is None:
        await callback_query.answer("Мастер не найден")
        return

    markup = build_master_schedule_keyboard(
        year, month, available_days, master_telegram_id
    )
    await callback_query.message.edit_reply_markup(reply_markup=markup)
    await callback_query.answer()


@router.callback_query(lambda c: c.data.startswith("sched:close:"))
async def schedule_close_handler(callback_query: CallbackQuery) -> None:
    _, _, schedule_message_id = callback_query.data.split(":", maxsplit=2)
    try:
        await callback_query.bot.delete_message(
            chat_id=callback_query.message.chat.id,
            message_id=int(schedule_message_id),
        )
    except TelegramBadRequest:
        pass

    try:
        await callback_query.message.delete()
    except TelegramBadRequest:
        pass

    await callback_query.answer()
