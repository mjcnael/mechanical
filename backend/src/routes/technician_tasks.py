from fastapi import APIRouter, Depends, HTTPException
from errors import AppError, ErrorCode
from models import technician_tasks
from schemas.auth import CurrentUser
from schemas.technician_task import (
    TaskStatusUpdate,
    TechnicianTask,
    TechnicianTaskCreate,
    TechnicianTaskUpdate,
    TechnicianTaskFilter
)
from services.auth import get_current_user, require_role

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
        status: str = "",
        _user: CurrentUser = Depends(
            require_role("foreman", error_code=ErrorCode.TASK_LIST_FORBIDDEN)
        )):
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
async def get_technician_task_by_id(
    task_id: int, user: CurrentUser = Depends(get_current_user)
):
    try:
        task = await technician_tasks.get_technician_task_by_id(task_id)
        if user.role == "technician" and task.technician_id != user.user_id:
            raise AppError(ErrorCode.TASK_CROSS_WORKSHOP_ACCESS)
        return task
    except AppError:
        raise
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@technician_tasks_router.post("/status", response_model=TechnicianTask)
async def update_technician_task_status(
    dto: TaskStatusUpdate,
    user: CurrentUser = Depends(
        require_role("technician", error_code=ErrorCode.TASK_STATUS_FOREIGN)
    ),
):
    try:
        task = await technician_tasks.get_technician_task_by_id(dto.task_id)
        if task.technician_id != user.user_id:
            raise AppError(ErrorCode.TASK_STATUS_FOREIGN)
        updated_task = await technician_tasks.update_technician_task_status(
            dto.task_id, dto.status
        )
        return updated_task
    except AppError as exc:
        if exc.error_code == ErrorCode.TASK_NOT_FOUND:
            raise AppError(ErrorCode.TASK_STATUS_NOT_FOUND)
        raise
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@technician_tasks_router.post("", response_model=TechnicianTask)
async def create_technician_task(
    dto: TechnicianTaskCreate,
    _user: CurrentUser = Depends(
        require_role("foreman", error_code=ErrorCode.TASK_CREATE_FORBIDDEN)
    ),
):
    return await technician_tasks.insert_technician_task(dto)


@technician_tasks_router.put("/{task_id}", response_model=TechnicianTask)
async def update_technician_task(
    task_id: int,
    dto: TechnicianTaskUpdate,
    _user: CurrentUser = Depends(
        require_role("foreman", error_code=ErrorCode.TASK_EDIT_FORBIDDEN)
    ),
):
    try:
        updated_task = await technician_tasks.update_technician_task(task_id, dto)
        return updated_task
    except AppError:
        raise
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
