from datetime import date

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from .booking_utils import get_available_time_slots, shift_month
from .calendar_keyboard import create_calendar_keyboard
from .confirmation_keyboard import create_confirmation_keyboard
from .master_keyboard import create_master_keyboard
from .service_keyboard import choice_service
from .states import BookingState
from .time_keyboard import create_time_keyboard


router = Router()

# Функция для сборки итогового текста подтверждения записи.
def build_booking_summary(data: dict) -> str:
    return (
        "Всё верно?\n"
        f"Услуга: {data.get('service')}\n"
        f"Дата: {data.get('date')}\n"
        f"Время: {data.get('time')}\n"
        f"Мастер: {data.get('master')}"
    )

    # Первый шаг записи: выбор услуги.
async def new_entry_handler(message: Message, state: FSMContext):
    # функция генерации клафиатуры услуг
    keyboard = choice_service()
    await state.set_state(BookingState.choosing_service)
    await message.answer(
        "Выбери услугу которая тебе нужна", reply_markup=keyboard
    )

# отлов выбора услуги и переход к выбору даты
@router.callback_query(lambda c: c.data.startswith("service_"))
async def service_callback_handler(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    # извликаем выбранную услугу и сегодняшнюю дату
    service = callback_query.data.split("_")[1]
    today = date.today()

    await state.update_data(service=service)
    await state.set_state(BookingState.choosing_date)
    await callback_query.message.edit_text(
        f"Ты выбрал услугу {service}.\nТеперь выбери дату:",
        # генерируем клавиатуру с календарем
        reply_markup=create_calendar_keyboard(today.year, today.month),
    )
    await callback_query.answer()


@router.callback_query(lambda c: c.data == "cal:ignore")
async def calendar_ignore_handler(callback_query: CallbackQuery):
    # Техническая кнопка-заглушка, ничего не делает.
    await callback_query.answer()


@router.callback_query(
    lambda c: c.data.startswith("cal:prev:")
    or c.data.startswith("cal:next:")
)
async def calendar_navigation_handler(callback_query: CallbackQuery):
    # Листает месяцы и не дает уйти в прошлые месяцы.
    _, action, year, month = callback_query.data.split(":")
    delta = -1 if action == "prev" else 1
    target_year, target_month = shift_month(int(year), int(month), delta)
    today = date.today()

    # Защита от ухода в прошлые месяцы.
    if date(target_year, target_month, 1) < date(today.year, today.month, 1):
        target_year = today.year
        target_month = today.month

    await callback_query.message.edit_reply_markup(
        reply_markup=create_calendar_keyboard(target_year, target_month)
    )
    await callback_query.answer()

# Отлов выбора дня и переход к выбору времени.
@router.callback_query(lambda c: c.data.startswith("cal:day:"))
async def calendar_day_handler(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    # После выбора даты переходим к выбору времени.
    _, _, year, month, day = callback_query.data.split(":")
    selected_date = date(int(year), int(month), int(day))
    available_slots = get_available_time_slots(selected_date)

    if not available_slots:
        # Защита: время могло стать недоступным
        # между кликом и обработкой.
        await callback_query.answer("На эту дату свободного времени нет")
        return

    await state.update_data(date=selected_date.isoformat())
    await state.set_state(BookingState.choosing_time)
    await callback_query.message.edit_text(
        f"Дата выбрана: {selected_date.strftime('%d.%m.%Y')}\nВыбери время:",
        reply_markup=create_time_keyboard(selected_date),
    )
    await callback_query.answer()

# Отлов выбора времени и переход к выбору мастера.
@router.callback_query(lambda c: c.data.startswith("time:"))
async def time_callback_handler(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    # После выбора времени переходим к выбору мастера.
    selected_time = callback_query.data.split(":", maxsplit=1)[1]
    await state.update_data(time=selected_time)
    await state.set_state(BookingState.choosing_master)

    await callback_query.message.edit_text(
        f"Время выбрано: {selected_time}\nВыбери мастера:",
        reply_markup=create_master_keyboard(),
    )
    await callback_query.answer()

# Отлов выбора мастера и переход к подтверждению записи.
@router.callback_query(lambda c: c.data.startswith("master:"))
async def master_callback_handler(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    # После выбора мастера показываем итоговое подтверждение.
    selected_master = callback_query.data.split(":", maxsplit=1)[1]
    await state.update_data(master=selected_master)
    await state.set_state(BookingState.confirming_booking)
    data = await state.get_data()

    await callback_query.message.edit_text(
        build_booking_summary(data),
        reply_markup=create_confirmation_keyboard(),
    )
    await callback_query.answer()

# Отлов подтверждения записи и финальное сообщение.
@router.callback_query(lambda c: c.data == "confirm:yes")
async def confirm_booking_handler(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    # Финальный шаг: подтверждаем запись и очищаем состояние.
    data = await state.get_data()

    await callback_query.message.edit_text(
        "Запись подтверждена!\n"
        f"Услуга: {data.get('service')}\n"
        f"Дата: {data.get('date')}\n"
        f"Время: {data.get('time')}\n"
        f"Мастер: {data.get('master')}"
    )
    await state.clear()
    await callback_query.answer("Готово")


@router.callback_query(lambda c: c.data == "confirm:cancel")
async def cancel_booking_handler(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    await callback_query.message.edit_text("Запись отменена")
    await state.clear()
    await callback_query.answer("Отменено")
