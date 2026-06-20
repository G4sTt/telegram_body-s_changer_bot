import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
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
                    bicep REAL,
                    forearm REAL,
                    shoulders REAL,
                    chest REAL,
                    waist REAL,
                    hip REAL,
                    calf REAL,
                    ass REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            print("✅ Таблица measurements готова к работе")

    async def save_measurement(self, user_id: int, part: str, value: float):
        """Сохранение или обновление замера"""
        async with self.pool.acquire() as conn:
            # Проверяем, есть ли пользователь в БД
            row = await conn.fetchrow('SELECT user_id FROM measurements WHERE user_id = $1', user_id)
            if not row:
                await conn.execute('INSERT INTO measurements (user_id) VALUES ($1)', user_id)

            # Список допустимых колонок (защита от SQL-инъекций)
            valid_parts = ['bicep', 'forearm', 'shoulders', 'chest', 'waist', 'hip', 'calf', 'ass']
            if part in valid_parts:
                # Динамический запрос (имя колонки подставляем через f-строку, значение через $1)
                query = f'''
                    UPDATE measurements 
                    SET {part} = $1, updated_at = CURRENT_TIMESTAMP 
                    WHERE user_id = $2
                '''
                await conn.execute(query, value, user_id)
                print(f"✅ Сохранено: user_id={user_id}, {part}={value}")

    async def get_measurements(self, user_id: int):
        """Получение всех замеров пользователя"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow('SELECT * FROM measurements WHERE user_id = $1', user_id)
            return row

    async def delete_user_data(self, user_id: int):
        """Удаление всех данных пользователя"""
        async with self.pool.acquire() as conn:
            await conn.execute('DELETE FROM measurements WHERE user_id = $1', user_id)