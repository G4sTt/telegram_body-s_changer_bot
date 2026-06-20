import asyncio
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

from states import BodyMeasurements
from db import Database

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BODY_TOKEN")
if not TOKEN:
    raise ValueError("TELEGRAM_BODY_TOKEN not set")

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())
db = Database()


# ==================== КОМАНДЫ ====================

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
    await message.answer("Какую часть тела хотите замерить?", reply_markup=inline_menu)


@dp.message(Command("cancel"))
async def cancel_handler(message: Message, state: FSMContext):
    """Отмена ввода"""
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("Нечего отменять — вы не вводите данные.")
        return
    await state.clear()
    await message.answer("❌ Действие отменено.")


@dp.message(Command("mydata"))
async def show_data(message: Message):
    """Просмотр сохранённых данных из БД"""
    user_id = message.from_user.id
    data = await db.get_measurements(user_id)

    if not data:
        await message.answer("У вас пока нет сохранённых данных. Используйте /body для начала замеров.")
        return

    text = "📊 Ваши замеры:\n"
    names = {
        "bicep": "Бицепс",
        "forearm": "Предплечье",
        "shoulders": "Плечи",
        "chest": "Грудь",
        "waist": "Талия",
        "hip": "Бёдра",
        "calf": "Икры",
        "ass": "Ягодицы"
    }
    for key, value in data.items():
        if key in names and value is not None:
            text += f"• {names[key]}: {value} см\n"

    await message.answer(text)


# ==================== КНОПКИ МЕНЮ ====================

@dp.callback_query(F.data == "upper_body")
async def process_upper_body(callback: CallbackQuery):
    inline_menu = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Обхват бицепса 💪", callback_data="upper_body_arm")],
        [InlineKeyboardButton(text="Обхват предплечья", callback_data="upper_body_forearm")],
        [InlineKeyboardButton(text="Обхват плеч", callback_data="upper_body_shoulders")],
        [InlineKeyboardButton(text="Обхват груди", callback_data="upper_body_chest")],
        [InlineKeyboardButton(text="Обхват талии", callback_data="upper_body_waist")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_menu")]
    ])
    await callback.message.answer("Какую часть верха хотите замерить?", reply_markup=inline_menu)
    await callback.answer()


@dp.callback_query(F.data == "lower_body")
async def process_lower_body(callback: CallbackQuery):
    inline_menu = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Обхват бедра", callback_data="lower_body_hip")],
        [InlineKeyboardButton(text="Обхват икры", callback_data="lower_body_calf")],
        [InlineKeyboardButton(text="Обхват ягодиц", callback_data="lower_body_ass")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_menu")]
    ])
    await callback.message.answer("Какую часть низа хотите замерить?", reply_markup=inline_menu)
    await callback.answer()


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


@dp.callback_query(F.data == "info")
async def process_info(callback: CallbackQuery):
    await callback.message.answer(
        "Инструкция:\n"
        "1. Выберите часть тела\n"
        "2. Введите замеры в сантиметрах (только число!)\n"
        "3. Для отмены ввода используйте /cancel\n"
        "4. Для просмотра данных используйте /mydata"
    )
    await callback.answer()


# ==================== ОБРАБОТЧИКИ КНОПОК ЗАМЕРОВ ====================
# ✅ У каждой функции уникальное имя и параметр state: FSMContext

@dp.callback_query(F.data == "upper_body_arm")
async def process_bicep(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "Вы выбрали замеры бицепса.\n"
        "Пожалуйста, напишите обхват вашего бицепса в сантиметрах (например: 42):"
    )
    await state.set_state(BodyMeasurements.waiting_for_bicep)
    await callback.answer()


@dp.callback_query(F.data == "upper_body_forearm")
async def process_forearm(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "Вы выбрали замеры предплечья.\n"
        "Пожалуйста, напишите обхват вашего предплечья в сантиметрах (например: 30):"
    )
    await state.set_state(BodyMeasurements.waiting_for_forearm)
    await callback.answer()


@dp.callback_query(F.data == "upper_body_shoulders")
async def process_shoulders(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "Вы выбрали замеры плеч.\n"
        "Пожалуйста, напишите обхват ваших плеч в сантиметрах (например: 120):"
    )
    await state.set_state(BodyMeasurements.waiting_for_shoulders)
    await callback.answer()


@dp.callback_query(F.data == "upper_body_chest")
async def process_chest(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "Вы выбрали замеры груди.\n"
        "Пожалуйста, напишите обхват вашей груди в сантиметрах (например: 100):"
    )
    await state.set_state(BodyMeasurements.waiting_for_chest)
    await callback.answer()


@dp.callback_query(F.data == "upper_body_waist")
async def process_waist(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "Вы выбрали замеры талии.\n"
        "Пожалуйста, напишите обхват вашей талии в сантиметрах (например: 80):"
    )
    await state.set_state(BodyMeasurements.waiting_for_waist)
    await callback.answer()


@dp.callback_query(F.data == "lower_body_hip")
async def process_hip(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "Вы выбрали замеры бедра.\n"
        "Пожалуйста, напишите обхват вашего бедра в сантиметрах (например: 60):"
    )
    await state.set_state(BodyMeasurements.waiting_for_hip)
    await callback.answer()


@dp.callback_query(F.data == "lower_body_calf")
async def process_calf(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "Вы выбрали замеры икры.\n"
        "Пожалуйста, напишите обхват вашей икры в сантиметрах (например: 40):"
    )
    await state.set_state(BodyMeasurements.waiting_for_calf)
    await callback.answer()


@dp.callback_query(F.data == "lower_body_ass")
async def process_ass(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "Вы выбрали замеры ягодиц.\n"
        "Пожалуйста, напишите обхват ваших ягодиц в сантиметрах (например: 100):"
    )
    await state.set_state(BodyMeasurements.waiting_for_ass)
    await callback.answer()


# ==================== ОБРАБОТЧИКИ ВВОДА ЧИСЕЛ ====================

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


@dp.message(StateFilter(BodyMeasurements.waiting_for_forearm))
async def input_forearm(message: Message, state: FSMContext):
    await process_measurement_input(message, state, "Обхват предплечья", "forearm")


@dp.message(StateFilter(BodyMeasurements.waiting_for_shoulders))
async def input_shoulders(message: Message, state: FSMContext):
    await process_measurement_input(message, state, "Обхват плеч", "shoulders")


@dp.message(StateFilter(BodyMeasurements.waiting_for_chest))
async def input_chest(message: Message, state: FSMContext):
    await process_measurement_input(message, state, "Обхват груди", "chest")


@dp.message(StateFilter(BodyMeasurements.waiting_for_waist))
async def input_waist(message: Message, state: FSMContext):
    await process_measurement_input(message, state, "Обхват талии", "waist")


@dp.message(StateFilter(BodyMeasurements.waiting_for_hip))
async def input_hip(message: Message, state: FSMContext):
    await process_measurement_input(message, state, "Обхват бедра", "hip")


@dp.message(StateFilter(BodyMeasurements.waiting_for_calf))
async def input_calf(message: Message, state: FSMContext):
    await process_measurement_input(message, state, "Обхват икры", "calf")


@dp.message(StateFilter(BodyMeasurements.waiting_for_ass))
async def input_ass(message: Message, state: FSMContext):
    await process_measurement_input(message, state, "Обхват ягодиц", "ass")


# ==================== ЗАПУСК ====================

async def on_startup():
    """Действия при запуске бота"""
    await db.create_pool()
    await db.init_db()
    print("✅ База данных PostgreSQL подключена!")


async def on_shutdown():
    """Действия при остановке бота"""
    await db.close_pool()
    print("🔌 База данных отключена.")


async def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    print('Бот запущен!')
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())