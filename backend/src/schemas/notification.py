from datetime import datetime

from pydantic import BaseModel


class Notification(BaseModel):
    notification_id: int
    recipient_role: str
    recipient_id: int
    task_id: int | None
    message: str
    is_read: bool
    created_at: datetime


class UnreadCount(BaseModel):
    unread_count: int
