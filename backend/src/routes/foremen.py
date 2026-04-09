from fastapi import APIRouter, Depends, HTTPException
from errors import AppError
from models import foremen
from schemas.foreman import Foreman, ForemanCreate, ForemanUpdate
from schemas.auth import CurrentUser
from services.auth import require_role

foremen_router = APIRouter(prefix="/foremen", tags=["Foremen"])


@foremen_router.get("", response_model=list[Foreman])
async def get_foremen(_: CurrentUser = Depends(require_role("foreman"))):
    return await foremen.get_foremen()


@foremen_router.get("/{foreman_id}", response_model=Foreman)
async def get_foreman_by_id(
    foreman_id: int, _: CurrentUser = Depends(require_role("foreman"))
):
    try:
        return await foremen.get_foreman_by_id(foreman_id)
    except AppError:
        raise
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@foremen_router.post("", response_model=Foreman)
async def create_foreman(
    dto: ForemanCreate, _: CurrentUser = Depends(require_role("foreman"))
):
    try:
        return await foremen.insert_foreman(dto)
    except AppError:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@foremen_router.put("/{foreman_id}", response_model=Foreman)
async def update_foreman(
    foreman_id: int,
    dto: ForemanUpdate,
    _: CurrentUser = Depends(require_role("foreman")),
):
    try:
        updated_foreman = await foremen.update_foreman(foreman_id, dto)
        return updated_foreman
    except AppError:
        raise
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
