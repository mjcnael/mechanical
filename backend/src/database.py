import asyncpg
from config import config


class Postgresql:
    def __init__(self, url) -> None:
        self.url = url

    async def connect(self):
        self.pool = await asyncpg.create_pool(self.url)
        await self.create_tables()

    async def disconnect(self):
        await self.pool.close()

    async def create_tables(self):
        create_tables_queries = [
            """
            CREATE TABLE IF NOT EXISTS foremen (
                foreman_id SERIAL PRIMARY KEY,
                full_name VARCHAR(100) NOT NULL,
                gender CHAR(1) CHECK (gender IN ('М', 'Ж')) NOT NULL,
                workshop VARCHAR(50),
                phone_number VARCHAR(11) UNIQUE NOT NULL
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS technicians (
                technician_id SERIAL PRIMARY KEY,
                specialization VARCHAR(50) NOT NULL,
                full_name VARCHAR(100) NOT NULL,
                gender CHAR(1) CHECK (gender IN ('М', 'Ж')) NOT NULL,
                phone_number VARCHAR(11) UNIQUE NOT NULL
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS technician_tasks (
                task_id SERIAL PRIMARY KEY,
                start_time VARCHAR(16) NOT NULL,
                end_time VARCHAR(16) NOT NULL,
                workshop VARCHAR(50) NOT NULL,
                foreman_id INTEGER NOT NULL REFERENCES foremen(foreman_id),
                technician_id INTEGER NOT NULL REFERENCES technicians(technician_id),
                task_description VARCHAR(500) NOT NULL,
                status VARCHAR(20) NOT NULL CHECK (status IN ('Не выполнено', 'В процессе', 'Выполнено', 'Отменено'))
            );
            """,
        ]

        async with self.pool.acquire() as connection:
            for query in create_tables_queries:
                await connection.execute(query)


database = Postgresql(
    f"postgres://{config.postgresql.USERNAME}:{config.postgresql.PASSWORD}@{config.postgresql.HOST}:{config.postgresql.PORT}/{config.postgresql.NAME}"
)
