import asyncio
import os
from aiogram import Bot, Dispatcher
from aiogram.filters import Command

bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
dp = Dispatcher()

@dp.message(Command("start"))
async def start(message):
    await message.answer(f"Привет,"
                         f"я бот который делает замеры твоего тела"
                         f"мои функции:"
                         f"/body - начать делать замеры")

async def main():
    print('Бот запущен!')
    await dp.start_polling()

if __name__ == '__main__':
    asyncio.run(main())