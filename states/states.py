from aiogram.fsm.state import State, StatesGroup


class DATAS(StatesGroup):
    first_name = State()
    last_name = State()
    lavozim = State()
    image = State()
    birth_day = State()