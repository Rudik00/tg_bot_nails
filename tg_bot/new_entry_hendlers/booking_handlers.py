from datetime import date, datetime

from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.exc import IntegrityError

from ..database.create_db import SessionLocal
from ..database.models_db import Client, MasterClient
from ..telegram_contact import build_contact_link_html, escape_html_text
from .booking_utils import get_available_time_slots, shift_month
from .calendar_keyboard import create_calendar_keyboard
from .confirmation_keyboard import create_confirmation_keyboard
from .master_keyboard import create_master_keyboard, get_master_by_telegram_id
from .service_keyboard import choice_service, get_service_by_id
from .states import BookingState
from .time_keyboard import create_time_keyboard


router = Router()

# Функция для сборки итогового текста подтверждения записи.


def build_booking_summary(data: dict) -> str:
    service_line = data.get("service_name") or data.get("service")
    price = data.get("service_price")
    duration = data.get("service_duration")
    master_line = data.get("master_name") or data.get("master")
    master_contact = build_contact_link_html(
        data.get("master_username"),
        data.get("master_telegram_id"),
        data.get("master_name") or "Связаться с мастером",
    )

    return (
        "Всё верно?\n"
        f"Услуга: {service_line}\n"
        f"Стоимость: {price if price is not None else '-'}\n"
        f"Длительность: {duration if duration is not None else '-'} мин\n"
        f"Дата: {data.get('date')}\n"
        f"Время: {data.get('time')}\n"
        f"Мастер: {master_line}\n"
        f"Ссылка для связи: {master_contact}"
    )


# Первый шаг записи: выбор услуги.
async def new_entry_handler(message: Message, state: FSMContext):
    # функция генерации клафиатуры услуг
    keyboard = await choice_service()
    if keyboard is None:
        await message.answer("Список услуг пока пуст")
        return

    await state.set_state(BookingState.choosing_service)
    await message.answer(
        "Выбери услугу которая тебе нужна", reply_markup=keyboard
    )


# отлов выбора услуги и переход к выбору даты
@router.callback_query(lambda c: c.data.startswith("service:"))
async def service_callback_handler(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    # извликаем выбранную услугу и сегодняшнюю дату
    service_id = int(callback_query.data.split(":", maxsplit=1)[1])
    service = await get_service_by_id(service_id)
    if service is None:
        await callback_query.answer("Услуга не найдена")
        return

    today = date.today()

    await state.update_data(
        service_id=service.id,
        service=service.name,
        service_name=service.name,
        service_price=service.price,
        service_duration=service.time_services,
    )
    await state.set_state(BookingState.choosing_date)
    await callback_query.message.edit_text(
        f"Ты выбрал услугу {service.name}.\nТеперь выбери дату:",
        # генерируем клавиатуру с календарем
        reply_markup=await create_calendar_keyboard(
            today.year, today.month
        ),
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
        reply_markup=await create_calendar_keyboard(
            target_year, target_month
        )
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
    data = await state.get_data()
    selected_date = date.fromisoformat(data["date"])
    master_keyboard = await create_master_keyboard(
        selected_date, selected_time
    )

    if master_keyboard is None:
        await callback_query.message.edit_text(
            "Свободных мастеров сейчас нет"
        )
        await callback_query.answer()
        return

    await state.update_data(time=selected_time)
    await state.set_state(BookingState.choosing_master)

    await callback_query.message.edit_text(
        f"Время выбрано: {selected_time}\nВыбери мастера:",
        reply_markup=master_keyboard,
    )
    await callback_query.answer()


# Отлов выбора мастера и переход к подтверждению записи.
@router.callback_query(lambda c: c.data.startswith("master:"))
async def master_callback_handler(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    # После выбора мастера показываем итоговое подтверждение.
    master_telegram_id = int(
        callback_query.data.split(":", maxsplit=1)[1]
    )
    selected_master = await get_master_by_telegram_id(master_telegram_id)
    if selected_master is None:
        await callback_query.answer("Мастер не найден")
        return

    await state.update_data(
        master=selected_master.name,
        master_name=selected_master.name,
        master_telegram_id=selected_master.telegram_id,
        master_username=selected_master.username,
    )
    await state.set_state(BookingState.confirming_booking)
    data = await state.get_data()

    await callback_query.message.edit_text(
        build_booking_summary(data),
        reply_markup=create_confirmation_keyboard(),
        parse_mode="HTML",
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
    master_telegram_id = data.get("master_telegram_id")
    service_id = data.get("service_id")
    booking_date = data.get("date")
    booking_time = data.get("time")

    if not all([master_telegram_id, service_id, booking_date, booking_time]):
        await callback_query.answer(
            "Не удалось подтвердить запись. Повторите запись заново."
        )
        await state.clear()
        return

    master = await get_master_by_telegram_id(int(master_telegram_id))
    if master is None:
        await callback_query.answer("Мастер не найден")
        return

    booking_date_obj = date.fromisoformat(booking_date)
    booking_time_obj = datetime.strptime(booking_time, "%H:%M").time()
    client_telegram_id = callback_query.from_user.id
    client_username = callback_query.from_user.username
    master_username = master.username

    try:
        async with SessionLocal() as session:
            async with session.begin():
                session.add(
                    MasterClient(
                        master_id=master.id,
                        booking_date=booking_date_obj,
                        booking_time=booking_time_obj,
                        service=(
                            data.get("service_name")
                            or data.get("service")
                            or "-"
                        ),
                        client_telegram_id=client_telegram_id,
                    )
                )
                session.add(
                    Client(
                        client_telegram_id=client_telegram_id,
                        client_username=client_username,
                        service_id=int(service_id),
                        booking_date=booking_date_obj,
                        booking_time=booking_time_obj,
                        master_telegram_id=int(master_telegram_id),
                        master_username=master_username,
                        master_name=master.name,
                    )
                )
    except IntegrityError:
        await callback_query.message.edit_text(
            "Этот слот уже заняли. Выбери другую дату или время."
        )
        await state.clear()
        await callback_query.answer("Слот занят")
        return

    service_price = data.get("service_price")
    service_duration = data.get("service_duration")
    price_text = service_price if service_price is not None else "-"
    duration_text = (
        f"{service_duration} мин"
        if service_duration is not None
        else "-"
    )
    service_text = escape_html_text(
        data.get("service_name") or data.get("service")
    )
    master_text = escape_html_text(
        data.get("master_name") or data.get("master")
    )
    client_contact = build_contact_link_html(
        client_username,
        client_telegram_id,
        "Связаться с клиентом",
    )
    master_contact = build_contact_link_html(
        master_username,
        int(master_telegram_id),
        master.name,
    )

    master_notification_text = (
        "Новая запись клиента\n"
        f"Дата: {escape_html_text(booking_date)}\n"
        f"Время: {escape_html_text(booking_time)}\n"
        f"Услуга: {service_text}\n"
        f"Стоимость: {escape_html_text(price_text)}\n"
        f"Длительность: {escape_html_text(duration_text)}\n"
        f"Ссылка для связи: {client_contact}"
    )

    try:
        await callback_query.bot.send_message(
            int(master_telegram_id),
            master_notification_text,
            parse_mode="HTML",
        )
    except TelegramBadRequest:
        # Если нельзя отправить сообщение мастеру,
        # запись в БД все равно сохранена.
        pass

    await callback_query.message.edit_text(
        "Запись подтверждена!\n"
        f"Услуга: {service_text}\n"
        f"Стоимость: {escape_html_text(price_text)}\n"
        f"Длительность: {escape_html_text(duration_text)}\n"
        f"Дата: {escape_html_text(data.get('date'))}\n"
        f"Время: {escape_html_text(data.get('time'))}\n"
        f"Мастер: {master_text}\n"
        f"Ссылка для связи: {master_contact}",
        parse_mode="HTML",
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
