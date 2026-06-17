import asyncio
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage  # ← Вот эта строка!

from states import BodyMeasurements
from db import Database

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BODY_TOKEN")
if not TOKEN:
    raise ValueError("TELEGRAM_BODY_TOKEN not set")

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())
db = Database()

@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "Привет!\n"
        "Я бот, который делает замеры твоего тела.\n\n"
        "Мои функции:\n"
        "/body - начать делать замеры\n"
        "/mydata - посмотреть сохранённые замеры\n"
        "/cancel - отменить ввод"
    )

@dp.message(Command("body"))
async def body(message: Message):
    inline_menu = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Верх тела 🧍‍♂️", callback_data="upper_body")],
        [InlineKeyboardButton(text="Низ тела 🦵", callback_data="lower_body")],
        [
            InlineKeyboardButton(text="Инструкция 📖", callback_data="info"),
            InlineKeyboardButton(text="Сайт 🌐", url="https://google.com")
        ]
    ])

    await message.answer(
        "Какую часть тела хотите замерить?",
        reply_markup=inline_menu
    )

@dp.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery):
    inline_menu = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Верх тела 🧍‍♂️", callback_data="upper_body")],
        [InlineKeyboardButton(text="Низ тела 🦵", callback_data="lower_body")],
        [
            InlineKeyboardButton(text="Инструкция 📖", callback_data="info"),
            InlineKeyboardButton(text="Сайт 🌐", url="https://google.com")
        ]
    ])
    await callback.message.edit_text(
        "Какую часть тела хотите замерить?",
        reply_markup=inline_menu
    )
    await callback.answer()

@dp.message(Command("cancel"))
async def cancel_handler(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("Нечего отменять — вы не вводите данные.")
        return
    await state.clear()
    await message.answer("❌ Действие отменено.")

@dp.message(Command("mydata"))
async def show_data(message: Message):
    user_id = message.from_user.id
    data = await db.get_measurements(user_id)

    if not data:
        await message.answer("У вас пока нет сохранённых данных. Используйте /body для начала замеров.")
        return

    text = "📊 Ваши замеры:\n"
    names = {
        "chest": "Грудь",
        "bicep": "Бицепс",
        "forearm": "Предплечье",
        "shoulders": "Плечи",
        "hips": "Бёдра"
    }
    for key, value in data.items():
        if key in names and value is not None:
            text += f"• {names[key]}: {value} см\n"

    await message.answer(text)

@dp.callback_query(F.data == "upper_body")
async def process_upper_body(callback: CallbackQuery):
    inline_menu = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Обхват бицепса", callback_data="upper_body_arm")],
        [InlineKeyboardButton(text="Обхват предплечья", callback_data="upper_body_forearm")],
        [InlineKeyboardButton(text="Обхват плеч", callback_data="upper_body_shoulders")],
        [InlineKeyboardButton(text="Обхват груди", callback_data="upper_body_chest")],
        [InlineKeyboardButton(text="Обхват талии", callback_data="upper_body_waist")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_menu")]
    ])

    await callback.message.answer(
        "Какую часть верха хотите замерить?",
        reply_markup=inline_menu
    )
    await callback.answer()

@dp.callback_query(F.data == "lower_body")
async def process_lower_body(callback: CallbackQuery):
    inline_menu = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Обхват бедра", callback_data="lower_body_hip")],
        [InlineKeyboardButton(text="Обхват икры", callback_data="lower_body_calf")],
        [InlineKeyboardButton(text="Обхват ягодиц", callback_data="lower_body_ass")],
        [
            InlineKeyboardButton(text="Инструкция 📖", callback_data="info"),
            InlineKeyboardButton(text="Сайт 🌐", url="https://google.com")
        ]
    ])

    await callback.message.answer(
        "Какую часть низа хотите замерить?",
        reply_markup=inline_menu
    )
    await callback.answer()

@dp.callback_query(F.data == "upper_body_forearm")
async def process_upper_body_forearm(callback: CallbackQuery):
    await callback.message.answer(
        "Вы выбрали замер предплечья.\n"
        "Пожалуйста, напишите обхват вашего предплечья в самой крупной части в сантиметрах:"
    )
    await callback.set_state(BodyMeasurements.waiting_for_forearm)
    await callback.answer()

@dp.callback_query(F.data == "upper_body_arm")
async def process_upper_body_arm(callback: CallbackQuery):
    await callback.message.answer(
        "Вы выбрали замер бицепса.\n"
        "Пожалуйста, напишите обхват вашего бицепса в самой крупной части в сантиметрах:"
    )
    await callback.set_state(BodyMeasurements.waiting_for_bicep)
    await callback.answer()

@dp.callback_query(F.data == "upper_body_shoulders")
async def process_upper_body_shoulders(callback: CallbackQuery):
    await callback.message.answer(
        "Вы выбрали замер плеч.\n"
        "Пожалуйста, напишите обхват ваших плеч в самой крупной части в сантиметрах:"
    )
    await callback.set_state(BodyMeasurements.waiting_for_shoulders)
    await callback.answer()

@dp.callback_query(F.data == "upper_body_chest")
async def process_upper_body_chest(callback: CallbackQuery):
    await callback.message.answer(
        "Вы выбрали замер груди.\n"
        "Пожалуйста, напишите обхват вашей груди в самой крупной части в сантиметрах:"
    )
    await callback.set_state(BodyMeasurements.waiting_for_chest)
    await callback.answer()

@dp.callback_query(F.data == "upper_body_waist")
async def process_upper_body_waist(callback: CallbackQuery):
    await callback.message.answer(
        "Вы выбрали замер талии.\n"
        "Пожалуйста, напишите обхват вашей талии в самой узкой части в сантиметрах:"
    )
    await callback.set_state(BodyMeasurements.waiting_for_waist)
    await callback.answer()

@dp.callback_query(F.data == "upper_body_calf")
async def process_upper_body_calf(callback: CallbackQuery):
    await callback.message.answer(
        "Вы выбрали замер икры.\n"
        "Пожалуйста, напишите обхват вашей икры в самой крупной части в сантиметрах:"
    )
    await callback.set_state(BodyMeasurements.waiting_for_calf)
    await callback.answer()

@dp.callback_query(F.data == "upper_body_hip")
async def process_upper_body_hip(callback: CallbackQuery):
    await callback.message.answer(
        "Вы выбрали замер бедра.\n"
        "Пожалуйста, напишите обхват вашего бедра в самой крупной части в сантиметрах:"
    )
    await callback.set_state(BodyMeasurements.waiting_for_hip)
    await callback.answer()

@dp.callback_query(F.data == "info")
async def process_info(callback: CallbackQuery):
    await callback.message.answer(
        "Инструкция:\n"
        "1. Выберите часть тела\n"
        "2. Введите замеры в сантиметрах\n"
    )
    await callback.answer()


async def process_measurement_input(message: Message, state: FSMContext,
                                    measurement_name: str, state_key: str):
    """Универсальный обработчик ввода замера"""
    try:
        value = float(message.text.replace(",", "."))  # Принимаем и запятую, и точку
        if value <= 0:
            await message.answer("❌ Значение должно быть больше 0. Попробуйте ещё раз:")
            return

        user_id = message.from_user.id

        # ✅ СОХРАНЯЕМ В БАЗУ ДАННЫХ
        await db.save_measurement(user_id, state_key, value)

        await message.answer(f"✅ {measurement_name} сохранён: {value} см")
        await state.clear()  # Сбрасываем состояние

    except ValueError:
        await message.answer("❌ Пожалуйста, введите число (например: 42.5). Попробуйте ещё раз:")
        # Состояние НЕ сбрасываем — бот продолжит ждать правильный ввод

@dp.message(StateFilter(BodyMeasurements.waiting_for_bicep))
async def input_bicep(message: Message, state: FSMContext):
    await process_measurement_input(message, state, "Обхват бицепса", "bicep")

async def main():
    print('Бот запущен!')
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())