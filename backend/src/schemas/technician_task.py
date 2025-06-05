from pydantic import BaseModel


class TaskStatusUpdate(BaseModel):
    task_id: int
    status: str


class TechnicianTask(BaseModel):
    task_id: int
    start_time: str
    end_time: str
    workshop: str
    foreman_id: int
    technician_id: int
    task_description: str
    status: str
    important: bool


class TechnicianTaskCreate(BaseModel):
    start_time: str
    end_time: str
    workshop: int
    foreman_id: int
    technician_id: int
    task_description: str
    important: bool


class TechnicianTaskUpdate(BaseModel):
    start_time: str
    end_time: str
    task_description: str
    important: bool
