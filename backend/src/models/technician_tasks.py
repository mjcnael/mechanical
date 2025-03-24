from database import database
from models import foremen
from schemas.technician_task import (
    TechnicianTask,
    TechnicianTaskCreate,
    TechnicianTaskUpdate,
)


async def get_technician_tasks():
    query = """
    SELECT task_id, start_time, end_time, workshop, foreman_id, technician_id, task_description, status 
    FROM technician_tasks
    ORDER BY task_id DESC;
    """
    async with database.pool.acquire() as connection:
        rows = await connection.fetch(query)
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
            )
            for record in rows
        ]
        return tasks


async def get_technician_tasks_by_technician_id(id: int):
    query = """
    SELECT task_id, start_time, end_time, workshop, foreman_id, technician_id, task_description, status 
    FROM technician_tasks
    WHERE technician_id = $1
    ORDER BY task_id DESC;
    """
    async with database.pool.acquire() as connection:
        rows = await connection.fetch(query, id)
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
            )
            for record in rows
        ]
        return tasks


async def get_technician_task_by_id(task_id: int):
    query = """
    SELECT task_id, start_time, end_time, workshop, foreman_id, technician_id, task_description, status 
    FROM technician_tasks
    WHERE task_id = $1;
    """
    async with database.pool.acquire() as connection:
        task = await connection.fetchrow(query, task_id)
        if task is None:
            raise Exception(f"Task with ID {task_id} not found.")
        return TechnicianTask(**task)


async def insert_technician_task(dto: TechnicianTaskCreate):
    foreman = await foremen.get_foreman_by_id(dto.workshop)

    query = """
    INSERT INTO technician_tasks (start_time, end_time, workshop, foreman_id, technician_id, task_description, status)
    VALUES ($1, $2, $3, $4, $5, $6, $7)
    RETURNING task_id, start_time, end_time, workshop, foreman_id, technician_id, task_description, status;
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
        )
        return TechnicianTask(**result)


async def update_technician_task(task_id: int, dto: TechnicianTaskUpdate):
    query = """
    UPDATE technician_tasks
    SET start_time = $1, end_time = $2, task_description = $3
    WHERE task_id = $4
    RETURNING task_id, start_time, end_time, workshop, foreman_id, technician_id, task_description, status;
    """
    async with database.pool.acquire() as connection:
        result = await connection.fetchrow(
            query,
            dto.start_time,
            dto.end_time,
            dto.task_description,
            task_id,
        )
        if result is None:
            raise Exception(f"Task with ID {task_id} not found.")
        return TechnicianTask(**result)


async def update_technician_task_status(task_id: int, status: str):
    query = """
    UPDATE technician_tasks
    SET status = $1
    WHERE task_id = $2
    RETURNING task_id, start_time, end_time, workshop, foreman_id, technician_id, task_description, status;
    """
    async with database.pool.acquire() as connection:
        result = await connection.fetchrow(
            query,
            status,
            task_id,
        )
        if result is None:
            raise Exception(f"Task with ID {task_id} not found.")
        return TechnicianTask(**result)
