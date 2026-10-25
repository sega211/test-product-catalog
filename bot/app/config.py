import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    bot_token: str
    admin_ids: frozenset[int]
    api_base_url: str


def load_settings() -> Settings:
    token = os.environ.get("BOT_TOKEN", "").strip()
    if not token or token == "replace_with_telegram_bot_token":
        raise RuntimeError("Не задан BOT_TOKEN — токен Telegram-бота")

    raw_admin_ids = os.environ.get("ADMIN_IDS", "").strip()
    if not raw_admin_ids:
        raise RuntimeError("Не задан ADMIN_IDS — Telegram ID администраторов")

    try:
        admin_ids = frozenset(
            int(value.strip())
            for value in raw_admin_ids.split(",")
            if value.strip()
        )
    except ValueError as exc:
        raise RuntimeError(
            "ADMIN_IDS должен содержать числовые Telegram ID через запятую"
        ) from exc

    if not admin_ids or any(user_id <= 0 for user_id in admin_ids):
        raise RuntimeError(
            "ADMIN_IDS должен содержать положительные Telegram ID"
        )

    api_base_url = os.environ.get(
        "API_BASE_URL",
        "http://127.0.0.1:8010",
    ).strip().rstrip("/")

    if not api_base_url:
        raise RuntimeError("Не задан API_BASE_URL — адрес backend сервера")

    return Settings(
        bot_token=token,
        admin_ids=admin_ids,
        api_base_url=api_base_url,
    )
