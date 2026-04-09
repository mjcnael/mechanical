from fastapi import APIRouter, Depends, HTTPException
from errors import AppError, ErrorCode
from models import technicians, technician_tasks
from schemas.auth import CurrentUser
from schemas.technician import Technician, TechnicianCreate, TechnicianUpdate
from schemas.technician_task import TechnicianTask
from services.auth import get_current_user, require_role

technicians_router = APIRouter(prefix="/technicians", tags=["Technicians"])


@technicians_router.get("", response_model=list[Technician])
async def get_technicians(_: CurrentUser = Depends(require_role("foreman"))):
    return await technicians.get_technicians()


@technicians_router.get("/{technician_id}", response_model=Technician)
async def get_technician_by_id(
    technician_id: int, user: CurrentUser = Depends(get_current_user)
):
    if user.role == "technician" and user.user_id != technician_id:
        raise AppError(ErrorCode.PROFILE_EDIT_FOREIGN)
    try:
        return await technicians.get_technician_by_id(technician_id)
    except AppError:
        raise
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@technicians_router.get("/{technician_id}/tasks", response_model=list[TechnicianTask])
async def get_tasks_by_technician_id(
    technician_id: int, user: CurrentUser = Depends(get_current_user)
):
    if user.role == "technician" and user.user_id != technician_id:
        raise AppError(ErrorCode.TASK_NOT_ASSIGNED_TO_USER)
    try:
        return await technician_tasks.get_technician_tasks_by_technician_id(
            technician_id,
            user.user_id if user.role == "foreman" else None,
        )
    except AppError:
        raise
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@technicians_router.post("", response_model=Technician)
async def create_technician(
    dto: TechnicianCreate, _: CurrentUser = Depends(require_role("foreman"))
):
    try:
        return await technicians.insert_technician(dto)
    except AppError:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@technicians_router.put("/{technician_id}", response_model=Technician)
async def update_technician(
    technician_id: int,
    dto: TechnicianUpdate,
    _: CurrentUser = Depends(require_role("foreman")),
):
    try:
        updated_technician = await technicians.update_technician(technician_id, dto)
        return updated_technician
    except AppError:
        raise
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
