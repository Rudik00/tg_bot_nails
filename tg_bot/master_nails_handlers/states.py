from aiogram.fsm.state import State, StatesGroup


class BookingState(StatesGroup):
    choosing_menu = State()
    choosing_work_days = State()
    choosing_week_days = State()