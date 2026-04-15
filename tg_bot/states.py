from aiogram.fsm.state import State, StatesGroup


class BookingState(StatesGroup):
    choosing_service = State()
    choosing_date = State()
    choosing_time = State()
    choosing_master = State()
