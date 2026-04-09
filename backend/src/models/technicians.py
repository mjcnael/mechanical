from database import database
from errors import AppError, ErrorCode
from schemas.technician import Technician, TechnicianCreate, TechnicianUpdate
from services.passwords import hash_password
from services.phone import is_valid_phone_number, normalize_phone_number


def validate_technician_payload(full_name: str, specialization: str, phone_number: str):
    if not full_name.strip() or phone_number.strip() == "":
        raise AppError(ErrorCode.REQUIRED_FIELDS_MISSING)
    if not specialization.strip():
        raise AppError(ErrorCode.TECHNICIAN_SPECIALIZATION_REQUIRED)
    if not is_valid_phone_number(phone_number):
        raise AppError(ErrorCode.INVALID_PHONE_FORMAT)
    if len(specialization) > 50:
        raise AppError(ErrorCode.INVALID_WORKSHOP_OR_SPECIALIZATION)


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
            raise AppError(ErrorCode.PROFILE_NOT_FOUND)
        return Technician(**technician)


async def insert_technician(dto: TechnicianCreate):
    phone_number = normalize_phone_number(dto.phone_number)
    validate_technician_payload(dto.full_name, dto.specialization, phone_number)
    if not dto.gender.strip() or not dto.password.strip():
        raise AppError(ErrorCode.REQUIRED_FIELDS_MISSING)
    query = """
    INSERT INTO technicians (specialization, full_name, gender, phone_number, password_hash) 
    VALUES ($1, $2, $3, $4, $5)
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
        exists = await connection.fetchrow(check_foreman_phone_query, phone_number)
        if exists:
            raise AppError(ErrorCode.PHONE_ALREADY_EXISTS)

        exists = await connection.fetchrow(check_technician_query, phone_number)
        if exists:
            raise AppError(ErrorCode.PHONE_ALREADY_EXISTS)

        result = await connection.fetchrow(
            query,
            dto.specialization,
            dto.full_name,
            dto.gender,
            phone_number,
            hash_password(dto.password),
        )
        return Technician(**result)


async def update_technician(technician_id: int, dto: TechnicianUpdate):
    phone_number = normalize_phone_number(dto.phone_number)
    validate_technician_payload(dto.full_name, dto.specialization, phone_number)
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
        exists = await connection.fetchrow(check_foreman_phone_query, phone_number)
        if exists:
            raise AppError(ErrorCode.PHONE_ALREADY_EXISTS)

        exists = await connection.fetchrow(check_technician_query, phone_number)
        if exists and technician_id != exists["technician_id"]:
            raise AppError(ErrorCode.PHONE_ALREADY_EXISTS)

        result = await connection.fetchrow(
            query,
            dto.specialization,
            dto.full_name,
            phone_number,
            technician_id,
        )
        if result is None:
            raise AppError(ErrorCode.PROFILE_NOT_FOUND)
        return Technician(**result)
