from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram import Router


from .states import BookingState
from ..database.add_work_days_db import add_work_days_db_handler
from ..database.user_verification import verification_master


router = Router()


async def records_work_days(
    message: Message,
    state: FSMContext,
    master_telegram_id: int,
):
    # Проверяем, является ли пользователь мастером
    is_master = await verification_master(master_telegram_id)
    if not is_master:
        await message.answer(
            "Извините, но вы не являетесь мастером и не можете "
            "добавлять рабочие дни."
        )
        return
    await state.set_state(BookingState.choosing_work_days)
    await message.answer(
        "Давай добавим рабочие дни в твой график! 💅\n"
        "Запиши через черту (/) дни недели, в которые ты работаешь.\n"
        "Например: пн/вт/ср/чт/пт\n"
    )


@router.message(BookingState.choosing_work_days)
async def process_work_days(message: Message, state: FSMContext):
    work_days = message.text.lower().split("/")
    # валидируем введенные дни недели
    valid_days = {"пн", "вт", "ср", "чт", "пт", "сб", "вс"}
    invalid_days = [day for day in work_days if day not in valid_days]
    if invalid_days:
        await message.answer(
            f"Некорректные дни недели: {', '.join(invalid_days)}"
        )
    else:
        master_id = message.from_user.id
        text = await add_work_days_db_handler(master_id, work_days)

        if text:
            await message.answer(
                f"Твои прабочие дни добавлены в график.\n"
                f"Работаешь в следующие дни: {', '.join(work_days)}"
            )
        else:
            await message.answer(
                "Произошла ошибка при добавлении рабочих дней. "
                "Попробуй еще раз."
            )
    await state.clear()  # Очищаем состояние после обработки данных
