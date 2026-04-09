from typing import Literal

from pydantic import BaseModel


UserRole = Literal["foreman", "technician"]


class LoginRequest(BaseModel):
    role: UserRole
    phone_number: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: UserRole
    user_id: int
    full_name: str


class CurrentUser(BaseModel):
    role: UserRole
    user_id: int
    phone_number: str
    full_name: str
    workshop: str | None = None
