import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

class Database:  # ← Обязательно с БОЛЬШОЙ буквы!
    def __init__(self):
        self.pool = None

    async def create_pool(self):
        """Создание пула подключений к БД"""
        self.pool = await asyncpg.create_pool(
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "your_password"),
            database=os.getenv("DB_NAME", "body_bot"),
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", 5432))
        )

    async def close_pool(self):
        """Закрытие пула подключений"""
        if self.pool:
            await self.pool.close()

    async def init_db(self):
        """Создание таблицы, если её нет"""
        async with self.pool.acquire() as conn:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS measurements (
                    user_id BIGINT PRIMARY KEY,
                    chest REAL,
                    bicep REAL,
                    forearm REAL,
                    shoulders REAL,
                    hips REAL
                )
            ''')

    async def save_measurement(self, user_id: int, part: str, value: float):
        """Сохранение или обновление замера"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow('SELECT user_id FROM measurements WHERE user_id = $1', user_id)
            if not row:
                await conn.execute('INSERT INTO measurements (user_id) VALUES ($1)', user_id)

            valid_parts = ['chest', 'bicep', 'forearm', 'shoulders', 'hips']
            if part in valid_parts:
                query = f'UPDATE measurements SET {part} = $1 WHERE user_id = $2'
                await conn.execute(query, value, user_id)

    async def get_measurements(self, user_id: int):
        """Получение всех замеров пользователя"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow('SELECT * FROM measurements WHERE user_id = $1', user_id)
            return row