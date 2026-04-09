from database import database
from errors import AppError, ErrorCode
from schemas.foreman import Foreman, ForemanCreate, ForemanUpdate
from services.passwords import hash_password
from services.phone import is_valid_phone_number, normalize_phone_number


def validate_foreman_payload(full_name: str, workshop: str, phone_number: str):
    if not full_name.strip() or phone_number.strip() == "":
        raise AppError(ErrorCode.REQUIRED_FIELDS_MISSING)
    if not is_valid_phone_number(phone_number):
        raise AppError(ErrorCode.INVALID_PHONE_FORMAT)
    if len(workshop) > 50:
        raise AppError(ErrorCode.INVALID_WORKSHOP)


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
            raise AppError(ErrorCode.USER_NOT_FOUND)
        return Foreman(**foreman)


async def insert_foreman(dto: ForemanCreate):
    phone_number = normalize_phone_number(dto.phone_number)
    validate_foreman_payload(dto.full_name, dto.workshop, phone_number)
    if not dto.gender.strip() or not dto.password.strip():
        raise AppError(ErrorCode.REQUIRED_FIELDS_MISSING)
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
        exists = await connection.fetchrow(check_technician_query, phone_number)
        if exists:
            raise AppError(ErrorCode.PHONE_ALREADY_EXISTS)

        exists = await connection.fetchrow(check_foreman_phone_query, phone_number)
        if exists:
            raise AppError(ErrorCode.PHONE_ALREADY_EXISTS)

        if len(dto.workshop) > 0:
            exists = await connection.fetchrow(
                check_foreman_workshop_query, dto.workshop
            )
            if exists:
                raise AppError(ErrorCode.INVALID_WORKSHOP)

        insert_query = """
        INSERT INTO foremen (full_name, gender, workshop, phone_number, password_hash) 
        VALUES ($1, $2, $3, $4, $5)
        RETURNING foreman_id, full_name, gender, workshop, phone_number;
        """

        result = await connection.fetchrow(
            insert_query,
            dto.full_name,
            dto.gender,
            dto.workshop,
            phone_number,
            hash_password(dto.password),
        )
        return Foreman(**result)


async def update_foreman(foreman_id: int, dto: ForemanUpdate):
    phone_number = normalize_phone_number(dto.phone_number)
    validate_foreman_payload(dto.full_name, dto.workshop, phone_number)
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
                raise AppError(ErrorCode.INVALID_WORKSHOP)

        exists = await connection.fetchrow(check_foreman_phone_query, phone_number)
        if exists and foreman_id != exists["foreman_id"]:
            raise AppError(ErrorCode.PHONE_ALREADY_EXISTS)

        exists = await connection.fetchrow(check_technician_query, phone_number)
        if exists:
            raise AppError(ErrorCode.PHONE_ALREADY_EXISTS)

        result = await connection.fetchrow(
            query,
            dto.full_name,
            dto.workshop,
            phone_number,
            foreman_id,
        )
        if result is None:
            raise AppError(ErrorCode.USER_NOT_FOUND)
        return Foreman(**result)
