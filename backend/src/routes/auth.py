from fastapi import APIRouter, Depends

from schemas.auth import CurrentUser, LoginRequest, TokenResponse
from services.auth import authenticate_user, create_access_token, get_current_user


auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post("/login", response_model=TokenResponse)
async def login(dto: LoginRequest):
    user = await authenticate_user(dto)
    return TokenResponse(
        access_token=create_access_token(user),
        role=user.role,
        user_id=user.user_id,
        full_name=user.full_name,
    )


@auth_router.get("/me", response_model=CurrentUser)
async def me(user: CurrentUser = Depends(get_current_user)):
    return user
