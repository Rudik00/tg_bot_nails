from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup, Message

from ..database.models_db import Client, Service
from ..database.remove_user_db import build_user_cancellation_keyboard
from ..database.remove_user_db import cancel_user_booking
from ..database.remove_user_db import get_user_booking_details
from ..database.remove_user_db import get_user_cancellable_bookings
from ..telegram_contact import build_contact_link_html, escape_html_text


router = Router()


def _build_cancel_confirmation_keyboard(
    booking_id: int,
) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Отменить запись",
                    callback_data=f"ucancel:confirm:{booking_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="Не отменять запись",
                    callback_data=f"ucancel:keep:{booking_id}",
                )
            ],
        ]
    )


def _build_booking_summary_html(booking: Client) -> str:
    service: Service | None = booking.service
    service_name = service.name if service is not None else "-"
    price_text = (
        str(service.price)
        if service is not None and service.price is not None
        else "-"
    )
    duration_text = (
        f"{service.time_services} мин"
        if service is not None and service.time_services is not None
        else "-"
    )
    master_contact = build_contact_link_html(
        booking.master_username,
        booking.master_telegram_id,
        booking.master_name,
    )

    return (
        "<b>Информация о записи</b>\n"
        f"Услуга: {escape_html_text(service_name)}\n"
        f"Стоимость: {escape_html_text(price_text)}\n"
        f"Длительность: {escape_html_text(duration_text)}\n"
        f"Дата: {booking.booking_date.strftime('%d.%m.%Y')}\n"
        f"Время: {booking.booking_time.strftime('%H:%M')}\n"
        f"Мастер: {escape_html_text(booking.master_name)}\n"
        f"Ссылка для связи: {master_contact}"
    )


def _build_master_cancellation_notification_html(
    booking: Client,
) -> str:
    service: Service | None = booking.service
    service_name = service.name if service is not None else "-"
    price_text = (
        str(service.price)
        if service is not None and service.price is not None
        else "-"
    )
    duration_text = (
        f"{service.time_services} мин"
        if service is not None and service.time_services is not None
        else "-"
    )
    client_contact = build_contact_link_html(
        booking.client_username,
        booking.client_telegram_id,
        "Связаться с клиентом",
    )

    return (
        "<b>Клиент отменил запись</b>\n"
        f"Услуга: {escape_html_text(service_name)}\n"
        f"Стоимость: {escape_html_text(price_text)}\n"
        f"Длительность: {escape_html_text(duration_text)}\n"
        f"Дата: {booking.booking_date.strftime('%d.%m.%Y')}\n"
        f"Время: {booking.booking_time.strftime('%H:%M')}\n"
        f"Клиент: {client_contact}"
    )


async def _send_cancellable_bookings(message: Message) -> None:
    bookings = await get_user_cancellable_bookings(message.from_user.id)
    if not bookings:
        await message.answer("У вас нет будущих записей для отмены.")
        return

    await message.answer(
        "Выберите запись, которую хотите отменить:",
        reply_markup=build_user_cancellation_keyboard(bookings),
    )


async def cancel_user_registration(
    message: Message,
    state: FSMContext,
) -> None:
    await state.clear()
    await _send_cancellable_bookings(message)


@router.callback_query(lambda c: c.data.startswith("ucancel:select:"))
async def select_cancellation_booking_handler(
    callback_query: CallbackQuery,
) -> None:
    booking_id = int(callback_query.data.split(":", maxsplit=2)[2])
    booking = await get_user_booking_details(
        callback_query.from_user.id,
        booking_id,
    )
    if booking is None:
        await callback_query.answer("Запись не найдена")
        return

    summary = _build_booking_summary_html(booking)
    await callback_query.message.edit_text(
        f"{summary}\n\nВы уверены, что хотите отменить запись?",
        reply_markup=_build_cancel_confirmation_keyboard(booking_id),
        parse_mode="HTML",
    )
    await callback_query.answer()


@router.callback_query(lambda c: c.data.startswith("ucancel:confirm:"))
async def confirm_cancellation_handler(
    callback_query: CallbackQuery,
) -> None:
    booking_id = int(callback_query.data.split(":", maxsplit=2)[2])
    booking = await get_user_booking_details(
        callback_query.from_user.id,
        booking_id,
    )
    if booking is None:
        await callback_query.message.edit_text("Запись уже недоступна.")
        await callback_query.answer("Запись не найдена")
        return

    summary = _build_booking_summary_html(booking)
    is_removed = await cancel_user_booking(
        callback_query.from_user.id,
        booking_id,
    )
    if not is_removed:
        await callback_query.message.edit_text("Не удалось отменить запись.")
        await callback_query.answer("Ошибка отмены")
        return

    await callback_query.message.edit_text(
        f"{summary}\n\n<b>Запись отменена.</b>",
        parse_mode="HTML",
    )
    try:
        await callback_query.bot.send_message(
            booking.master_telegram_id,
            _build_master_cancellation_notification_html(booking),
            parse_mode="HTML",
        )
    except TelegramBadRequest:
        pass
    await callback_query.answer("Запись отменена")


@router.callback_query(lambda c: c.data.startswith("ucancel:keep:"))
async def keep_cancellation_handler(
    callback_query: CallbackQuery,
) -> None:
    await callback_query.message.edit_text("Запись не отменена.")
    await _send_cancellable_bookings(callback_query.message)
    await callback_query.answer("Отмена не выполнена")
