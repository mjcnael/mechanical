from database import database
from schemas.notification import Notification


async def create_notification(
    recipient_role: str,
    recipient_id: int,
    task_id: int | None,
    message: str,
) -> Notification:
    query = """
    INSERT INTO notifications (recipient_role, recipient_id, task_id, message)
    VALUES ($1, $2, $3, $4)
    RETURNING notification_id, recipient_role, recipient_id, task_id, message, is_read, created_at;
    """
    async with database.pool.acquire() as connection:
        notification = await connection.fetchrow(
            query,
            recipient_role,
            recipient_id,
            task_id,
            message,
        )
    return Notification(**notification)


async def get_notifications(recipient_role: str, recipient_id: int) -> list[Notification]:
    query = """
    SELECT notification_id, recipient_role, recipient_id, task_id, message, is_read, created_at
    FROM notifications
    WHERE recipient_role = $1 AND recipient_id = $2
    ORDER BY created_at DESC, notification_id DESC;
    """
    async with database.pool.acquire() as connection:
        rows = await connection.fetch(query, recipient_role, recipient_id)
    return [Notification(**row) for row in rows]


async def get_unread_count(recipient_role: str, recipient_id: int) -> int:
    query = """
    SELECT COUNT(*) AS unread_count
    FROM notifications
    WHERE recipient_role = $1 AND recipient_id = $2 AND is_read = FALSE;
    """
    async with database.pool.acquire() as connection:
        row = await connection.fetchrow(query, recipient_role, recipient_id)
    return row["unread_count"]


async def mark_notification_as_read(
    notification_id: int,
    recipient_role: str,
    recipient_id: int,
) -> Notification:
    query = """
    UPDATE notifications
    SET is_read = TRUE
    WHERE notification_id = $1 AND recipient_role = $2 AND recipient_id = $3
    RETURNING notification_id, recipient_role, recipient_id, task_id, message, is_read, created_at;
    """
    async with database.pool.acquire() as connection:
        notification = await connection.fetchrow(
            query,
            notification_id,
            recipient_role,
            recipient_id,
        )
    if notification is None:
        raise Exception(f"Уведомление {notification_id} не найдено")
    return Notification(**notification)
