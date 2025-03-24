from database import database
from schemas.foreman import Foreman, ForemanCreate, ForemanUpdate


async def get_foremen():
    query = """
    SELECT foreman_id, full_name, gender, workshop, phone_number
    FROM foremen
    ORDER BY foreman_id ASC;
    """
    async with database.pool.acquire() as connection:
        rows = await connection.fetch(query)
        foremen = [
            Foreman(
                foreman_id=record["foreman_id"],
                full_name=record["full_name"],
                gender=record["gender"],
                workshop=record["workshop"],
                phone_number=record["phone_number"],
            )
            for record in rows
        ]
        return foremen


async def get_foreman_by_id(foreman_id: int):
    query = """
    SELECT foreman_id, full_name, gender, workshop, phone_number
    FROM foremen
    WHERE foreman_id = $1;
    """
    async with database.pool.acquire() as connection:
        foreman = await connection.fetchrow(query, foreman_id)
        if foreman is None:
            raise Exception(f"Foreman with ID {foreman_id} not found.")
        return Foreman(**foreman)


async def insert_foreman(dto: ForemanCreate):
    check_technician_query = """
    SELECT technician_id
    FROM technicians 
    WHERE phone_number = $1 
    LIMIT 1;
    """

    check_foreman_phone_query = """
    SELECT foreman_id
    FROM foremen 
    WHERE phone_number = $1 
    LIMIT 1;
    """

    check_foreman_workshop_query = """
    SELECT foreman_id
    FROM foremen 
    WHERE workshop = $1 
    LIMIT 1;
    """

    async with database.pool.acquire() as connection:
        exists = await connection.fetchrow(check_technician_query, dto.phone_number)
        if exists:
            raise Exception(
                f"Номер телефона записан на технического работника {exists['technician_id']}"
            )

        exists = await connection.fetchrow(check_foreman_phone_query, dto.phone_number)
        if exists:
            raise Exception(
                f"Номер телефона записан на начальника цеха {exists['foreman_id']}"
            )

        if len(dto.workshop) > 0:
            exists = await connection.fetchrow(
                check_foreman_workshop_query, dto.workshop
            )
            if exists:
                raise Exception(
                    f"Цех находится под управлением начальника {exists['foreman_id']}"
                )

        insert_query = """
        INSERT INTO foremen (full_name, gender, workshop, phone_number) 
        VALUES ($1, $2, $3, $4)
        RETURNING foreman_id, full_name, gender, workshop, phone_number;
        """

        result = await connection.fetchrow(
            insert_query,
            dto.full_name,
            dto.gender,
            dto.workshop,
            dto.phone_number,
        )
        return Foreman(**result)


async def update_foreman(foreman_id: int, dto: ForemanUpdate):
    query = """
    UPDATE foremen
    SET full_name = $1, workshop = $2, phone_number = $3
    WHERE foreman_id = $4
    RETURNING foreman_id, full_name, gender, workshop, phone_number;
    """

    check_technician_query = """
    SELECT technician_id
    FROM technicians 
    WHERE phone_number = $1 
    LIMIT 1;
    """

    check_foreman_workshop_query = """
    SELECT foreman_id
    FROM foremen 
    WHERE workshop = $1 
    LIMIT 1;
    """

    check_foreman_phone_query = """
    SELECT foreman_id
    FROM foremen 
    WHERE phone_number = $1 
    LIMIT 1;
    """

    async with database.pool.acquire() as connection:
        if len(dto.workshop) > 0:
            exists = await connection.fetchrow(
                check_foreman_workshop_query, dto.workshop
            )
            if exists and foreman_id != exists["foreman_id"]:
                raise Exception(
                    f"Цех находится под управлением начальника {exists['foreman_id']}"
                )

        exists = await connection.fetchrow(check_foreman_phone_query, dto.phone_number)
        if exists and foreman_id != exists["foreman_id"]:
            raise Exception(
                f"Номер телефона записан на начальника цеха {exists['foreman_id']}"
            )

        exists = await connection.fetchrow(check_technician_query, dto.phone_number)
        if exists:
            raise Exception(
                f"Номер телефона записан на технического работника {exists['technician_id']}"
            )

        result = await connection.fetchrow(
            query,
            dto.full_name,
            dto.workshop,
            dto.phone_number,
            foreman_id,
        )
        if result is None:
            raise Exception(f"Foreman with ID {foreman_id} not found.")
        return Foreman(**result)
