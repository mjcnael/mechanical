from pydantic import BaseModel


class Technician(BaseModel):
    technician_id: int
    specialization: str
    full_name: str
    gender: str
    phone_number: str


class TechnicianCreate(BaseModel):
    specialization: str
    full_name: str
    gender: str
    phone_number: str


class TechnicianUpdate(BaseModel):
    specialization: str
    full_name: str
    phone_number: str
