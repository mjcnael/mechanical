from pydantic import BaseModel


class Foreman(BaseModel):
    foreman_id: int
    full_name: str
    gender: str
    workshop: str
    phone_number: str


class ForemanCreate(BaseModel):
    full_name: str
    gender: str
    workshop: str
    phone_number: str


class ForemanUpdate(BaseModel):
    full_name: str
    workshop: str
    phone_number: str
