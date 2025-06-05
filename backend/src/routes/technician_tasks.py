from fastapi import APIRouter, HTTPException
from models import technician_tasks
from schemas.technician_task import (
    TaskStatusUpdate,
    TechnicianTask,
    TechnicianTaskCreate,
    TechnicianTaskUpdate,
    TechnicianTaskFilter
)
from pydantic.main import create_model

technician_tasks_router = APIRouter(
    prefix="/technician-tasks", tags=["Technician Tasks"]
)


@technician_tasks_router.get("", response_model=list[TechnicianTask])
async def get_technician_tasks(
        date_start: str = "",
        date_end: str = "",
        workshop: str = "",
        technician_name: str = "",
        foreman_name: str = "",
        status: str = ""):
    d = {
        'date_start': date_start,
        'date_end': date_end,
        'workshop': workshop,
        'technician_name': technician_name,
        'foreman_name': foreman_name,
        'status': status

    }
    prop = TechnicianTaskFilter(**d)
    return await technician_tasks.get_technician_tasks(prop)


@technician_tasks_router.get("/{task_id}", response_model=TechnicianTask)
async def get_technician_task_by_id(task_id: int):
    try:
        return await technician_tasks.get_technician_task_by_id(task_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@technician_tasks_router.post("/status", response_model=TechnicianTask)
async def update_technician_task_status(dto: TaskStatusUpdate):
    try:
        updated_task = await technician_tasks.update_technician_task_status(
            dto.task_id, dto.status
        )
        return updated_task
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@technician_tasks_router.post("", response_model=TechnicianTask)
async def create_technician_task(dto: TechnicianTaskCreate):
    return await technician_tasks.insert_technician_task(dto)


@technician_tasks_router.put("/{task_id}", response_model=TechnicianTask)
async def update_technician_task(task_id: int, dto: TechnicianTaskUpdate):
    try:
        updated_task = await technician_tasks.update_technician_task(task_id, dto)
        return updated_task
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
