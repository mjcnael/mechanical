from datetime import datetime

from database import database
from errors import AppError, ErrorCode
from models import foremen
from schemas.technician_task import (
    TechnicianTask,
    TechnicianTaskCreate,
    TechnicianTaskUpdate,
    TechnicianTaskFilter,
)
from services import notifications


TASK_DATE_FORMAT = "%d.%m.%Y %H:%M"
TASK_STATUSES = {"Не выполнено", "В процессе", "Выполнено", "Отменено"}


def parse_task_datetime(
    value: str, error_code: ErrorCode = ErrorCode.INVALID_TASK_DEADLINE
):
    try:
        return datetime.strptime(value, TASK_DATE_FORMAT)
    except ValueError:
        raise AppError(error_code)


def validate_task_window(start_time: str, end_time: str, error_code: ErrorCode):
    start = parse_task_datetime(start_time)
    end = parse_task_datetime(end_time)
    if end <= start:
        raise AppError(error_code)


def validate_task_description(description: str, error_code: ErrorCode):
    if not description.strip():
        raise AppError(ErrorCode.TASK_DESCRIPTION_REQUIRED)
    if len(description) > 500:
        raise AppError(error_code)


async def ensure_technician_exists(technician_id: int):
    query = """
    SELECT technician_id
    FROM technicians
    WHERE technician_id = $1;
    """
    async with database.pool.acquire() as connection:
        technician = await connection.fetchrow(query, technician_id)
    if technician is None:
        raise AppError(ErrorCode.TECHNICIAN_NOT_FOUND)


async def get_technician_tasks(
    filter: TechnicianTaskFilter, foreman_id: int | None = None
):
    if filter.date_start:
        parse_task_datetime(filter.date_start, ErrorCode.INVALID_FILTER_PARAMS)
    if filter.date_end:
        parse_task_datetime(filter.date_end, ErrorCode.INVALID_FILTER_PARAMS)

    start_date = filter.date_start if filter.date_start != "" else "01.01.2000 00:00"
    end_date = filter.date_end if filter.date_end != "" else "01.01.2033 00:00"

    query = """
    SELECT ts.task_id, ts.start_time, ts.end_time, ts.workshop, ts.foreman_id, ts.technician_id, ts.task_description, ts.status, ts.important
    FROM technician_tasks ts
    INNER JOIN technicians t USING(technician_id)
    INNER JOIN foremen f USING(foreman_id)
    WHERE ts.workshop LIKE '%' || $1 || '%'
          AND f.full_name LIKE '%' || $2 || '%'
          AND t.full_name LIKE '%' || $3 || '%'
          AND ts.status LIKE '%' || $4 || '%'
          AND TO_TIMESTAMP(ts.start_time,'DD-mm-YYYY HH24:MI') BETWEEN TO_TIMESTAMP($5,'DD-mm-YYYY HH24:MI')
          AND TO_TIMESTAMP($6,'DD-mm-YYYY HH24:MI')
          AND ($7::INTEGER IS NULL OR ts.foreman_id = $7)
    ORDER BY task_id DESC;
    """
    async with database.pool.acquire() as connection:
        rows = await connection.fetch(
            query,
            filter.workshop,
            filter.foreman_name,
            filter.technician_name,
            filter.status,
            start_date,
            end_date,
            foreman_id,
        )
        tasks = [
            TechnicianTask(
                task_id=record["task_id"],
                start_time=record["start_time"],
                end_time=record["end_time"],
                workshop=record["workshop"],
                foreman_id=record["foreman_id"],
                technician_id=record["technician_id"],
                task_description=record["task_description"],
                status=record["status"],
                important=record["important"],
            )
            for record in rows
        ]
        return tasks


async def get_technician_tasks_by_technician_id(
    id: int, foreman_id: int | None = None
):
    query = """
    SELECT task_id, start_time, end_time, workshop, foreman_id, technician_id, task_description, status, important

    FROM technician_tasks
    WHERE technician_id = $1 AND ($2::INTEGER IS NULL OR foreman_id = $2)
    ORDER BY task_id DESC;
    """
    async with database.pool.acquire() as connection:
        rows = await connection.fetch(query, id, foreman_id)
        tasks = [
            TechnicianTask(
                task_id=record["task_id"],
                start_time=record["start_time"],
                end_time=record["end_time"],
                workshop=record["workshop"],
                foreman_id=record["foreman_id"],
                technician_id=record["technician_id"],
                task_description=record["task_description"],
                status=record["status"],
                important=record["important"],
            )
            for record in rows
        ]
        return tasks


async def get_technician_task_by_id(task_id: int):
    query = """
    SELECT task_id, start_time, end_time, workshop, foreman_id, technician_id, task_description, status, important
 
    FROM technician_tasks
    WHERE task_id = $1;
    """
    async with database.pool.acquire() as connection:
        task = await connection.fetchrow(query, task_id)
        if task is None:
            raise AppError(ErrorCode.TASK_NOT_FOUND)
        return TechnicianTask(**task)


async def insert_technician_task(dto: TechnicianTaskCreate):
    if not dto.technician_id:
        raise AppError(ErrorCode.TECHNICIAN_REQUIRED)
    validate_task_window(
        dto.start_time,
        dto.end_time,
        ErrorCode.INVALID_TASK_DEADLINE,
    )
    validate_task_description(dto.task_description, ErrorCode.INVALID_TASK_EDIT_DATA)
    await ensure_technician_exists(dto.technician_id)
    foreman = await foremen.get_foreman_by_id(dto.foreman_id)
    query = """
    INSERT INTO technician_tasks (start_time, end_time, workshop, foreman_id, technician_id, task_description, status, important)
    VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
    RETURNING task_id, start_time, end_time, workshop, foreman_id, technician_id, task_description, status, important
    """
    async with database.pool.acquire() as connection:
        result = await connection.fetchrow(
            query,
            dto.start_time,
            dto.end_time,
            foreman.workshop,
            dto.foreman_id,
            dto.technician_id,
            dto.task_description,
            "Не выполнено",
            dto.important,
        )
    task = TechnicianTask(**result)
    await notifications.create_notification(
        "technician",
        task.technician_id,
        task.task_id,
        f"Вам назначена задача №{task.task_id}",
    )
    return task


async def update_technician_task(task_id: int, dto: TechnicianTaskUpdate):
    validate_task_window(
        dto.start_time,
        dto.end_time,
        ErrorCode.INVALID_TASK_EDIT_DATA,
    )
    validate_task_description(dto.task_description, ErrorCode.INVALID_TASK_EDIT_DATA)
    query = """
    UPDATE technician_tasks
    SET start_time = $1, end_time = $2, task_description = $3, important = $4
    WHERE task_id = $5
    RETURNING task_id, start_time, end_time, workshop, foreman_id, technician_id, task_description, status, important
    """
    async with database.pool.acquire() as connection:
        result = await connection.fetchrow(
            query,
            dto.start_time,
            dto.end_time,
            dto.task_description,
            dto.important,
            task_id,
        )
        if result is None:
            raise AppError(ErrorCode.TASK_NOT_FOUND)
        return TechnicianTask(**result)


async def update_technician_task_status(task_id: int, status: str):
    if status not in TASK_STATUSES:
        raise AppError(ErrorCode.INVALID_TASK_STATUS)
    query = """
    UPDATE technician_tasks
    SET status = $1
    WHERE task_id = $2
    RETURNING task_id, start_time, end_time, workshop, foreman_id, technician_id, task_description, status, important;
    """
    async with database.pool.acquire() as connection:
        result = await connection.fetchrow(
            query,
            status,
            task_id,
        )
        if result is None:
            raise AppError(ErrorCode.TASK_STATUS_NOT_FOUND)
    task = TechnicianTask(**result)
    await notifications.create_notification(
        "foreman",
        task.foreman_id,
        task.task_id,
        f"Статус задачи №{task.task_id} изменён на '{task.status}'",
    )
    return task
