from config import config
import uvicorn
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from errors import (
    AppError,
    app_error_handler,
    http_exception_handler,
    validation_exception_handler,
)
from routes import (
    auth_router,
    foremen_router,
    notifications_router,
    technician_tasks_router,
    technicians_router,
)
from database import database


@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    yield
    await database.disconnect()


app = FastAPI(lifespan=lifespan)
app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

app.include_router(auth_router)
app.include_router(foremen_router)
app.include_router(technicians_router)
app.include_router(technician_tasks_router)
app.include_router(notifications_router)

origins = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=config.startup.HOST,
        port=config.startup.PORT,
        reload=config.startup.RELOAD,
    )
