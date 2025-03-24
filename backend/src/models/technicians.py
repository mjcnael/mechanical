from database import database
from schemas.technician import Technician, TechnicianCreate, TechnicianUpdate


async def get_technicians():
    query = """
    SELECT technician_id, specialization, full_name, gender, phone_number 
    FROM technicians
    ORDER BY technician_id ASC;
    """
    async with database.pool.acquire() as connection:
        rows = await connection.fetch(query)
        technicians = [
            Technician(
                technician_id=record["technician_id"],
                specialization=record["specialization"],
                full_name=record["full_name"],
                gender=record["gender"],
                phone_number=record["phone_number"],
            )
            for record in rows
        ]
        return technicians


async def get_technician_by_id(technician_id: int):
    query = """
    SELECT technician_id, specialization, full_name, gender, phone_number
    FROM technicians
    WHERE technician_id = $1;
    """
    async with database.pool.acquire() as connection:
        technician = await connection.fetchrow(query, technician_id)
        if technician is None:
            raise Exception(f"Технический работник {technician_id} не найден")
        return Technician(**technician)


async def insert_technician(dto: TechnicianCreate):
    query = """
    INSERT INTO technicians (specialization, full_name, gender, phone_number) 
    VALUES ($1, $2, $3, $4)
    RETURNING technician_id, specialization, full_name, gender, phone_number;
    """

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

    async with database.pool.acquire() as connection:
        exists = await connection.fetchrow(check_foreman_phone_query, dto.phone_number)
        if exists:
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
            dto.specialization,
            dto.full_name,
            dto.gender,
            dto.phone_number,
        )
        return Technician(**result)


async def update_technician(technician_id: int, dto: TechnicianUpdate):
    query = """
    UPDATE technicians
    SET specialization = $1, full_name = $2, phone_number = $3
    WHERE technician_id = $4
    RETURNING technician_id, specialization, full_name, gender, phone_number;
    """

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

    async with database.pool.acquire() as connection:
        exists = await connection.fetchrow(check_foreman_phone_query, dto.phone_number)
        if exists:
            raise Exception(
                f"Номер телефона записан на начальника цеха {exists['foreman_id']}"
            )

        exists = await connection.fetchrow(check_technician_query, dto.phone_number)
        if exists and technician_id != exists["technician_id"]:
            raise Exception(
                f"Номер телефона записан на технического работника {exists['technician_id']}"
            )

        result = await connection.fetchrow(
            query,
            dto.specialization,
            dto.full_name,
            dto.phone_number,
            technician_id,
        )
        if result is None:
            raise Exception(f"Technician with ID {technician_id} not found.")
        return Technician(**result)
