FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY . ./app

WORKDIR /app

RUN uv sync

CMD ["uv", "run", "src/main.py"]
