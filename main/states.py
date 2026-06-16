from aiogram.fsm.state import State, StatesGroup

class BodyMeasurements(StatesGroup):
    waiting_for_bicep = State()       # Ожидание ввода обхвата бицепса
    waiting_for_forearm = State()     # Ожидание ввода обхвата предплечья
    waiting_for_shoulders = State()   # Ожидание ввода обхвата плеч
    waiting_for_chest = State()       # Ожидание ввода обхвата груди
    waiting_for_hip = State()        # Ожидание ввода обхвата бедер
    waiting_for_calf = State()
    waiting_for_waist = State()
    waiting_for_ass = State()