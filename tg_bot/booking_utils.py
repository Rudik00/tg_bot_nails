from datetime import date, datetime


TIME_SLOTS = ["10:00", "12:00", "14:00", "16:00", "18:00"]


def shift_month(year: int, month: int, delta: int) -> tuple[int, int]:
    # Переключает месяц вперед/назад с учетом смены года.
    month += delta
    if month < 1:
        return year - 1, 12
    if month > 12:
        return year + 1, 1
    return year, month


def get_available_time_slots(selected_date: date) -> list[str]:
    # Возвращает только те слоты, которые еще не наступили.
    now = datetime.now()
    available_slots: list[str] = []

    for slot in TIME_SLOTS:
        slot_time = datetime.strptime(slot, "%H:%M").time()
        slot_datetime = datetime.combine(selected_date, slot_time)
        if selected_date > now.date() or slot_datetime > now:
            available_slots.append(slot)

    return available_slots
