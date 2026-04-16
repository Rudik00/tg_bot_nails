from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram import Router

from .states import BookingState
from ..database.add_week_days_db import add_week_days_db_handler
from ..database.user_verification import verification_master

router = Router()


async def records_week_days(
    message: Message,
    state: FSMContext,
    master_telegram_id: int,
):
    # Проверяем, является ли пользователь мастером
    is_master = await verification_master(master_telegram_id)
    if not is_master:
        await message.answer(
            "Извините, но вы не являетесь мастером и не можете "
            "добавлять выходные дни."
        )
        return
    
    await state.set_state(BookingState.choosing_week_days)
    await message.answer(
        "Давай добавим выходные дни в твой график! 💅\n"
        "Вводи дни когда хочешь выходной\n"
        "Правила отправки сообщения:\n"
        "Первое число это день, а второе месяц. \n"
        "Например: 01.05, 06.05, 16.06\n"
    )


@router.message(BookingState.choosing_week_days)
async def process_week_days(message: Message, state: FSMContext):
    week_days = message.text.split(",")
    # валидируем введенные дни недели
    valid_format = True
    for day in week_days:
        if not day.strip().count(".") == 1:
            valid_format = False
            break
        day_part, month_part = day.strip().split(".")
        if not (day_part.isdigit() and month_part.isdigit()):
            valid_format = False
            break
        day_num = int(day_part)
        month_num = int(month_part)
        if not (1 <= day_num <= 31 and 1 <= month_num <= 12):
            valid_format = False
            break

    if not valid_format:
        await message.answer(
            "Некорректный формат даты. Пожалуйста, вводи дни в формате ДД.ММ, разделяя их запятыми.\n/master_info для возвращения в меню."
        )
    else:
        master_id = message.from_user.id
        answer = await add_week_days_db_handler(master_id, week_days)
        if answer:
            await message.answer(
                f"Твои выходные дни добавлены в график.\n"
                f"Выходные дни: {', '.join(week_days)}"
            )
        else:
            await message.answer(
                "Произошла ошибка при добавлении выходных дней. "
                "Попробуй еще раз."
            )
    await state.clear()  # Очищаем состояние после обработки данных