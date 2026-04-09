__all__ = [
    "auth_router",
    "foremen_router",
    "notifications_router",
    "technician_tasks_router",
    "technicians_router",
]

from routes.auth import auth_router
from routes.foremen import foremen_router
from routes.notifications import notifications_router
from routes.technician_tasks import technician_tasks_router
from routes.technicians import technicians_router
