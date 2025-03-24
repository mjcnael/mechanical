from fastapi import APIRouter, HTTPException
from models import foremen
from schemas.foreman import Foreman, ForemanCreate, ForemanUpdate

foremen_router = APIRouter(prefix="/foremen", tags=["Foremen"])


@foremen_router.get("", response_model=list[Foreman])
async def get_foremen():
    return await foremen.get_foremen()


@foremen_router.get("/{foreman_id}", response_model=Foreman)
async def get_foreman_by_id(foreman_id: int):
    try:
        return await foremen.get_foreman_by_id(foreman_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@foremen_router.post("", response_model=Foreman)
async def create_foreman(dto: ForemanCreate):
    try:
        return await foremen.insert_foreman(dto)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@foremen_router.put("/{foreman_id}", response_model=Foreman)
async def update_foreman(foreman_id: int, dto: ForemanUpdate):
    try:
        updated_foreman = await foremen.update_foreman(foreman_id, dto)
        return updated_foreman
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
