from fastapi import APIRouter, HTTPException
from models import technician_tasks
from schemas.technician_task import (
    TaskStatusUpdate,
    TechnicianTask,
    TechnicianTaskCreate,
    TechnicianTaskUpdate,
)

technician_tasks_router = APIRouter(
    prefix="/technician-tasks", tags=["Technician Tasks"]
)


@technician_tasks_router.get("", response_model=list[TechnicianTask])
async def get_technician_tasks():
    return await technician_tasks.get_technician_tasks()


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
