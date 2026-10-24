FROM mcr.microsoft.com/devcontainers/python:3.12-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY backend/requirements.txt /app/backend/requirements.txt

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r /app/backend/requirements.txt

COPY alembic.ini /app/alembic.ini
COPY backend /app/backend

WORKDIR /app

ENV PYTHONPATH=/app/backend

EXPOSE 8010

CMD ["uvicorn", "app.main:app", "--app-dir", "/app/backend", "--host", "0.0.0.0", "--port", "8010"]
