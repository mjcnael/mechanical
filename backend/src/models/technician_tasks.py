import logging

from database import database
from models import foremen
from schemas.technician_task import (
    TechnicianTask,
    TechnicianTaskCreate,
    TechnicianTaskUpdate,
    TechnicianTaskFilter
)

async def get_technician_tasks(filter: TechnicianTaskFilter):
    start_date = filter.date_start if filter.date_start!="" else "01.01.2000 00:00"
    end_date = filter.date_end if filter.date_end!="" else "01.01.2033 00:00"

    query = f"""
    SELECT ts.task_id, ts.start_time, ts.end_time, ts.workshop, ts.foreman_id, ts.technician_id, ts.task_description, ts.status
    FROM technician_tasks ts
    INNER JOIN technicians t USING(technician_id)
    INNER JOIN foremen f USING(foreman_id)
    WHERE ts.workshop LIKE '%{filter.workshop}%' AND f.full_name LIKE '%{filter.foreman_name}%' AND
          t.full_name LIKE '%{filter.technician_name}%' AND ts.status LIKE '%{filter.status}%' AND
          TO_TIMESTAMP(ts.start_time,'DD-mm-YYYY HH24:MI') BETWEEN TO_TIMESTAMP('{start_date}','DD-mm-YYYY HH24:MI')
          AND TO_TIMESTAMP('{end_date}','DD-mm-YYYY HH24:MI')
    ORDER BY task_id DESC;
    """
    print(query)
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
                important=record["important"],
            )
            for record in rows
        ]
        return tasks


async def get_technician_tasks_by_technician_id(id: int):
    query = """
    SELECT task_id, start_time, end_time, workshop, foreman_id, technician_id, task_description, status, important

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
            raise Exception(f"Task with ID {task_id} not found.")
        return TechnicianTask(**task)


async def insert_technician_task(dto: TechnicianTaskCreate):
    foreman = await foremen.get_foreman_by_id(dto.workshop)

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
        )
        return TechnicianTask(**result)


async def update_technician_task(task_id: int, dto: TechnicianTaskUpdate):
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
            raise Exception(f"Task with ID {task_id} not found.")
        return TechnicianTask(**result)


async def update_technician_task_status(task_id: int, status: str):
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
            raise Exception(f"Task with ID {task_id} not found.")
        return TechnicianTask(**result)
