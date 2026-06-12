import asyncio
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command
from magic_filter import F

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BODY_TOKEN")
if not TOKEN:
    raise ValueError("TELEGRAM_BODY_TOKEN not set")

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "Привет!\n"
        "Я бот, который делает замеры твоего тела.\n\n"
        "Мои функции:\n"
        "/body - начать делать замеры"
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

@dp.callback_query(F.data == "upper_body")
async def process_upper_body(callback: CallbackQuery):
    inline_menu = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Обхват бицепса", callback_data="upper_body_arm")],
        [InlineKeyboardButton(text="Обхват предплечья", callback_data="upper_body_forearm")],
        [InlineKeyboardButton(text="Обхват плеч", callback_data="upper_body_shoulders")],
        [
            InlineKeyboardButton(text="Инструкция 📖", callback_data="info"),
            InlineKeyboardButton(text="Сайт 🌐", url="https://google.com")
        ]
    ])

    await callback.message.answer(
        "Какую часть верха хотите замерить?",
        reply_markup=inline_menu
    )
    await callback.answer()

@dp.callback_query(F.data == "lower_body")
async def process_lower_body(callback: CallbackQuery):
    await callback.message.answer(
        "Вы выбрали замеры нижней части тела.\n"
        "Пожалуйста, напишите ваш обхват бедер в сантиметрах (например: 100):"
    )
    await callback.answer()

@dp.callback_query(F.data == "upper_body_forearm")
async def process_upper_body_forearm(callback: CallbackQuery):
    await callback.message.answer(
        "Вы выбрали замеры предплечья.\n"
        "Пожалуйста, напишите ваш обхват предплечья в самой крупной части в сантиметрах (например: 42):"
    )
    await callback.answer()

@dp.callback_query(F.data == "upper_body_arm")
async def process_upper_body_forearm(callback: CallbackQuery):
    await callback.message.answer(
        "Вы выбрали замеры бицепса.\n"
        "Пожалуйста, напишите ваш обхват предплечья в самой крупной части в сантиметрах (например: 42):"
    )
    await callback.answer()

@dp.callback_query(F.data == "upper_body_shoulders")
async def process_upper_body_forearm(callback: CallbackQuery):
    await callback.message.answer(
        "Вы выбрали замеры плеч.\n"
        "Пожалуйста, напишите ваш обхват предплечья в самой крупной части в сантиметрах (например: 122):"
    )
    await callback.answer()

@dp.callback_query(F.data == "info")
async def process_info(callback: CallbackQuery):
    await callback.message.answer(
        "Инструкция:\n"
        "1. Выберите часть тела\n"
        "2. Введите замеры в сантиметрах\n"
        "3. Получите рекомендации"
    )
    await callback.answer()

async def main():
    print('Бот запущен!')
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())