from fastapi import APIRouter, HTTPException
from models import technicians, technician_tasks
from schemas.technician import Technician, TechnicianCreate, TechnicianUpdate
from schemas.technician_task import TechnicianTask

technicians_router = APIRouter(prefix="/technicians", tags=["Technicians"])


@technicians_router.get("", response_model=list[Technician])
async def get_technicians():
    return await technicians.get_technicians()


@technicians_router.get("/{technician_id}", response_model=Technician)
async def get_technician_by_id(technician_id: int):
    try:
        return await technicians.get_technician_by_id(technician_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@technicians_router.get("/{technician_id}/tasks", response_model=list[TechnicianTask])
async def get_tasks_by_technician_id(technician_id: int):
    try:
        return await technician_tasks.get_technician_tasks_by_technician_id(
            technician_id
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@technicians_router.post("", response_model=Technician)
async def create_technician(dto: TechnicianCreate):
    try:
        return await technicians.insert_technician(dto)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@technicians_router.put("/{technician_id}", response_model=Technician)
async def update_technician(technician_id: int, dto: TechnicianUpdate):
    try:
        updated_technician = await technicians.update_technician(technician_id, dto)
        return updated_technician
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
