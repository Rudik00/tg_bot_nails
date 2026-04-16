from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram import Router


from .states import BookingState


router = Router()


async def records_work_days(message: Message, state: FSMContext):
    await state.set_state(BookingState.choosing_work_days)
    await message.answer("Давай добавим рабочие дни в твой график! 💅\n"
                         "Запиши через черту (/) дни недели, в которые ты работаешь.\n"
                         "Например: Пн/Вт/Ср/Чт/Пт\n")


@router.message(BookingState.choosing_work_days)
async def process_work_days(message: Message, state: FSMContext):
    work_days = message.text.split("/")
    # Здесь можно добавить валидацию введенных дней недели
    await message.answer(f"Ты выбрал рабочие дни: {', '.join(work_days)}")
    await state.clear()  # Очищаем состояние после обработки данных