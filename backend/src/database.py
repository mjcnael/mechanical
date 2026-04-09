import asyncpg
from config import config
from services.passwords import hash_password, verify_password
from services.phone import normalize_phone_number, phone_number_variants


DEFAULT_FOREMAN = {
    "full_name": "Данюк Кирилл Константинович",
    "gender": "М",
    "workshop": "Администрация",
    "phone_number": normalize_phone_number("89000000000"),
    "password": "user123",
}


class Postgresql:
    def __init__(self, url) -> None:
        self.url = url

    async def connect(self):
        self.pool = await asyncpg.create_pool(self.url)
        await self.create_tables()
        await self.seed_default_foreman()

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
                phone_number VARCHAR(16) UNIQUE NOT NULL,
                password_hash TEXT
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS technicians (
                technician_id SERIAL PRIMARY KEY,
                specialization VARCHAR(50) NOT NULL,
                full_name VARCHAR(100) NOT NULL,
                gender CHAR(1) CHECK (gender IN ('М', 'Ж')) NOT NULL,
                phone_number VARCHAR(16) UNIQUE NOT NULL,
                password_hash TEXT
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
                status VARCHAR(20) NOT NULL CHECK (status IN ('Не выполнено', 'В процессе', 'Выполнено', 'Отменено')),
                important BOOLEAN NOT NULL DEFAULT FALSE
            );
            """,
            """
            ALTER TABLE foremen
            ADD COLUMN IF NOT EXISTS password_hash TEXT;
            """,
            """
            ALTER TABLE foremen
            ALTER COLUMN phone_number TYPE VARCHAR(16);
            """,
            """
            ALTER TABLE technicians
            ADD COLUMN IF NOT EXISTS password_hash TEXT;
            """,
            """
            ALTER TABLE technicians
            ALTER COLUMN phone_number TYPE VARCHAR(16);
            """,
            """
            CREATE TABLE IF NOT EXISTS notifications (
                notification_id SERIAL PRIMARY KEY,
                recipient_role VARCHAR(20) NOT NULL CHECK (recipient_role IN ('foreman','technician')),
                recipient_id INTEGER NOT NULL,
                task_id INTEGER REFERENCES technician_tasks(task_id),
                message VARCHAR(255) NOT NULL,
                is_read BOOLEAN NOT NULL DEFAULT FALSE,
                created_at TIMESTAMP NOT NULL DEFAULT NOW()
            );
            """,
            """
            UPDATE foremen f
            SET phone_number = '+7' || SUBSTRING(f.phone_number FROM 2)
            WHERE f.phone_number ~ '^8[0-9]{10}$'
              AND NOT EXISTS (
                  SELECT 1
                  FROM foremen existing
                  WHERE existing.phone_number = '+7' || SUBSTRING(f.phone_number FROM 2)
              );
            """,
            """
            UPDATE technicians t
            SET phone_number = '+7' || SUBSTRING(t.phone_number FROM 2)
            WHERE t.phone_number ~ '^8[0-9]{10}$'
              AND NOT EXISTS (
                  SELECT 1
                  FROM technicians existing
                  WHERE existing.phone_number = '+7' || SUBSTRING(t.phone_number FROM 2)
              );
            """,
        ]

        async with self.pool.acquire() as connection:
            for query in create_tables_queries:
                await connection.execute(query)

    async def seed_default_foreman(self):
        query = """
        SELECT foreman_id, password_hash
        FROM foremen
        WHERE phone_number = ANY($1::TEXT[])
        LIMIT 1;
        """
        update_query = """
        UPDATE foremen
        SET full_name = $1, gender = $2, workshop = $3, phone_number = $4, password_hash = $5
        WHERE foreman_id = $6;
        """
        insert_query = """
        INSERT INTO foremen (full_name, gender, workshop, phone_number, password_hash)
        VALUES ($1, $2, $3, $4, $5);
        """

        async with self.pool.acquire() as connection:
            existing = await connection.fetchrow(
                query,
                phone_number_variants(DEFAULT_FOREMAN["phone_number"]),
            )
            password_hash_value = existing["password_hash"] if existing else None
            has_expected_password = existing and verify_password(
                DEFAULT_FOREMAN["password"],
                password_hash_value,
            )

            hashed_password = (
                password_hash_value
                if has_expected_password
                else hash_password(DEFAULT_FOREMAN["password"])
            )
            if existing:
                await connection.execute(
                    update_query,
                    DEFAULT_FOREMAN["full_name"],
                    DEFAULT_FOREMAN["gender"],
                    DEFAULT_FOREMAN["workshop"],
                    DEFAULT_FOREMAN["phone_number"],
                    hashed_password,
                    existing["foreman_id"],
                )
                return

            await connection.execute(
                insert_query,
                DEFAULT_FOREMAN["full_name"],
                DEFAULT_FOREMAN["gender"],
                DEFAULT_FOREMAN["workshop"],
                DEFAULT_FOREMAN["phone_number"],
                hashed_password,
            )


database = Postgresql(
    f"postgres://{config.postgresql.USERNAME}:{config.postgresql.PASSWORD}@{config.postgresql.HOST}:{config.postgresql.PORT}/{config.postgresql.NAME}"
)
