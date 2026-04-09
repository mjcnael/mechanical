from fastapi import APIRouter, Depends, HTTPException

from schemas.auth import CurrentUser
from schemas.notification import Notification, UnreadCount
from services.auth import get_current_user
from services import notifications


notifications_router = APIRouter(prefix="/notifications", tags=["Notifications"])


@notifications_router.get("", response_model=list[Notification])
async def get_notifications(user: CurrentUser = Depends(get_current_user)):
    return await notifications.get_notifications(user.role, user.user_id)


@notifications_router.get("/unread-count", response_model=UnreadCount)
async def get_unread_count(user: CurrentUser = Depends(get_current_user)):
    unread_count = await notifications.get_unread_count(user.role, user.user_id)
    return UnreadCount(unread_count=unread_count)


@notifications_router.post("/{notification_id}/read", response_model=Notification)
async def read_notification(
    notification_id: int,
    user: CurrentUser = Depends(get_current_user),
):
    try:
        return await notifications.mark_notification_as_read(
            notification_id,
            user.role,
            user.user_id,
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
