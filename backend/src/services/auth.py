from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError

from config import config
from database import database
from errors import AppError, ErrorCode
from schemas.auth import CurrentUser, LoginRequest
from services.passwords import verify_password
from services.phone import phone_number_variants


bearer_scheme = HTTPBearer(auto_error=False)


def create_access_token(user: CurrentUser) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=config.jwt.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {
        "sub": str(user.user_id),
        "role": user.role,
        "phone_number": user.phone_number,
        "full_name": user.full_name,
        "workshop": user.workshop,
        "exp": expires_at,
    }
    return jwt.encode(payload, config.jwt.SECRET_KEY, algorithm=config.jwt.ALGORITHM)


async def authenticate_user(dto: LoginRequest) -> CurrentUser:
    if dto.role == "foreman":
        query = """
        SELECT foreman_id AS user_id, phone_number, full_name, workshop, password_hash
        FROM foremen
        WHERE phone_number = ANY($1::TEXT[]);
        """
    else:
        query = """
        SELECT technician_id AS user_id, phone_number, full_name, NULL AS workshop, password_hash
        FROM technicians
        WHERE phone_number = ANY($1::TEXT[]);
        """

    async with database.pool.acquire() as connection:
        user = await connection.fetchrow(query, phone_number_variants(dto.phone_number))

    if not user or not verify_password(dto.password, user["password_hash"]):
        raise AppError(ErrorCode.UNAUTHORIZED)

    return CurrentUser(
        role=dto.role,
        user_id=user["user_id"],
        phone_number=user["phone_number"],
        full_name=user["full_name"],
        workshop=user["workshop"],
    )


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)]
) -> CurrentUser:
    if credentials is None:
        raise AppError(ErrorCode.UNAUTHORIZED)

    try:
        payload = jwt.decode(
            credentials.credentials,
            config.jwt.SECRET_KEY,
            algorithms=[config.jwt.ALGORITHM],
        )
        user_id = int(payload["sub"])
        role = payload["role"]
        if role not in ("foreman", "technician"):
            raise AppError(ErrorCode.UNKNOWN_USER_ROLE)
    except (InvalidTokenError, KeyError, TypeError, ValueError):
        raise AppError(ErrorCode.INVALID_CURRENT_USER)

    return CurrentUser(
        role=role,
        user_id=user_id,
        phone_number=payload["phone_number"],
        full_name=payload["full_name"],
        workshop=payload.get("workshop"),
    )


def require_role(*roles: str, error_code: ErrorCode = ErrorCode.TASK_LIST_FORBIDDEN):
    async def dependency(
        user: Annotated[CurrentUser, Depends(get_current_user)]
    ) -> CurrentUser:
        if user.role not in roles:
            raise AppError(error_code)
        return user

    return dependency
