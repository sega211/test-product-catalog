FROM mcr.microsoft.com/devcontainers/python:3.12-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY bot/requirements.txt /app/bot/requirements.txt

RUN pip install --no-cache-dir -r /app/bot/requirements.txt

COPY bot/app /app/bot/app

ENV PYTHONPATH=/app/bot

CMD ["python", "-m", "app.main"]
