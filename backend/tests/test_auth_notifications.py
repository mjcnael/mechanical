import os
from uuid import uuid4

import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient

os.environ.setdefault("APP_CONFIG__POSTGRESQL__HOST", "localhost")
os.environ.setdefault("APP_CONFIG__POSTGRESQL__PORT", "5432")
os.environ.setdefault("APP_CONFIG__JWT__SECRET_KEY", "test-secret-with-at-least-32-bytes")

from database import database
from main import app
from services.passwords import hash_password


pytestmark = pytest.mark.asyncio


@pytest.fixture
async def client():
    suffix = uuid4().hex[:8]
    phone_digits = str(uuid4().int)[:7]
    foreman_phone = f"+7900{phone_digits}"
    technician_phone = f"+7910{phone_digits}"
    password = "secret123"
    seeded_ids: dict[str, int] = {}

    try:
        async with LifespanManager(app):
            async with database.pool.acquire() as connection:
                foreman = await connection.fetchrow(
                    """
                    INSERT INTO foremen (full_name, gender, workshop, phone_number, password_hash)
                    VALUES ($1, 'М', $2, $3, $4)
                    RETURNING foreman_id;
                    """,
                    "Иванов Иван Иванович",
                    f"Цех {suffix}",
                    foreman_phone,
                    hash_password(password),
                )
                technician = await connection.fetchrow(
                    """
                    INSERT INTO technicians (specialization, full_name, gender, phone_number, password_hash)
                    VALUES ('Слесарь', $1, 'М', $2, $3)
                    RETURNING technician_id;
                    """,
                    "Петров Петр Петрович",
                    technician_phone,
                    hash_password(password),
                )
                seeded_ids["foreman_id"] = foreman["foreman_id"]
                seeded_ids["technician_id"] = technician["technician_id"]

            transport = ASGITransport(app=app)
            async with AsyncClient(
                transport=transport, base_url="http://test"
            ) as async_client:
                async_client.test_data = {
                    "foreman_phone": foreman_phone,
                    "technician_phone": technician_phone,
                    "password": password,
                    **seeded_ids,
                }
                yield async_client
            async with database.pool.acquire() as connection:
                await connection.execute(
                    "DELETE FROM notifications WHERE recipient_id = $1 OR recipient_id = $2;",
                    seeded_ids["foreman_id"],
                    seeded_ids["technician_id"],
                )
                await connection.execute(
                    "DELETE FROM technician_tasks WHERE foreman_id = $1 OR technician_id = $2;",
                    seeded_ids["foreman_id"],
                    seeded_ids["technician_id"],
                )
                await connection.execute(
                    "DELETE FROM technicians WHERE technician_id = $1;",
                    seeded_ids["technician_id"],
                )
                await connection.execute(
                    "DELETE FROM foremen WHERE foreman_id = $1;",
                    seeded_ids["foreman_id"],
                )
    except OSError as exc:
        pytest.skip(f"Postgres is not available for integration tests: {exc}")


async def login(client: AsyncClient, role: str) -> dict:
    phone_key = "foreman_phone" if role == "foreman" else "technician_phone"
    response = await client.post(
        "/auth/login",
        json={
            "role": role,
            "phone_number": client.test_data[phone_key],
            "password": client.test_data["password"],
        },
    )
    assert response.status_code == 200
    return response.json()


async def create_task(client: AsyncClient, foreman_token: str) -> dict:
    response = await client.post(
        "/technician-tasks",
        headers={"Authorization": f"Bearer {foreman_token}"},
        json={
            "start_time": "01.01.2026 10:00",
            "end_time": "01.01.2026 11:00",
            "foreman_id": client.test_data["foreman_id"],
            "technician_id": client.test_data["technician_id"],
            "task_description": "Проверить оборудование",
            "important": False,
        },
    )
    assert response.status_code == 200
    return response.json()


async def test_login_foreman_success(client: AsyncClient):
    token = await login(client, "foreman")
    assert token["role"] == "foreman"
    assert token["user_id"] == client.test_data["foreman_id"]
    assert token["token_type"] == "bearer"


async def test_default_foreman_login_success(client: AsyncClient):
    response = await client.post(
        "/auth/login",
        json={
            "role": "foreman",
            "phone_number": "89000000000",
            "password": "user123",
        },
    )

    assert response.status_code == 200
    token = response.json()
    assert token["role"] == "foreman"
    assert token["full_name"] == "Данюк Кирилл Константинович"


async def test_login_technician_success(client: AsyncClient):
    token = await login(client, "technician")
    assert token["role"] == "technician"
    assert token["user_id"] == client.test_data["technician_id"]


async def test_protected_endpoint_without_token_returns_401(client: AsyncClient):
    response = await client.get("/technician-tasks")
    assert response.status_code == 401


async def test_technician_cannot_create_task(client: AsyncClient):
    token = await login(client, "technician")
    response = await client.post(
        "/technician-tasks",
        headers={"Authorization": f"Bearer {token['access_token']}"},
        json={
            "start_time": "01.01.2026 10:00",
            "end_time": "01.01.2026 11:00",
            "foreman_id": client.test_data["foreman_id"],
            "technician_id": client.test_data["technician_id"],
            "task_description": "Проверить оборудование",
            "important": False,
        },
    )
    assert response.status_code == 403


async def test_foreman_creates_task_and_technician_gets_notification(
    client: AsyncClient,
):
    foreman = await login(client, "foreman")
    technician = await login(client, "technician")
    task = await create_task(client, foreman["access_token"])

    response = await client.get(
        "/notifications",
        headers={"Authorization": f"Bearer {technician['access_token']}"},
    )
    assert response.status_code == 200
    notifications = response.json()
    assert notifications[0]["task_id"] == task["task_id"]
    assert notifications[0]["message"] == f"Вам назначена задача №{task['task_id']}"


async def test_technician_changes_own_task_status_and_foreman_gets_notification(
    client: AsyncClient,
):
    foreman = await login(client, "foreman")
    technician = await login(client, "technician")
    task = await create_task(client, foreman["access_token"])

    status_response = await client.post(
        "/technician-tasks/status",
        headers={"Authorization": f"Bearer {technician['access_token']}"},
        json={"task_id": task["task_id"], "status": "В процессе"},
    )
    assert status_response.status_code == 200
    assert status_response.json()["status"] == "В процессе"

    response = await client.get(
        "/notifications",
        headers={"Authorization": f"Bearer {foreman['access_token']}"},
    )
    assert response.status_code == 200
    assert response.json()[0]["message"] == (
        f"Статус задачи №{task['task_id']} изменён на 'В процессе'"
    )
