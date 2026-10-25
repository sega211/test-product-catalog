# Test Product Catalog

Демонстрационный каталог товаров, разработанный в рамках тестового задания. Проект показывает взаимодействие frontend-приложения, REST API, PostgreSQL, объектного хранилища MinIO и Telegram-бота.

**Это демонстрационный проект, а не действующий интернет-магазин.** Товары и изображения используются в демонстрационных целях.

## Возможности

- Просмотр каталога товаров с изображениями.
- Получение данных о товарах через REST API.
- Хранение данных о товарах в PostgreSQL.
- Хранение изображений в объектном хранилище MinIO.
- Добавление товаров через Telegram-бота пользователями с административными правами.
- Открытие веб-каталога из Telegram.
- Запуск компонентов проекта с помощью Docker Compose.
- Управление схемой базы данных с помощью Alembic.

## Архитектура

Проект состоит из пяти сервисов:

| Сервис | Назначение |
|---|---|
| `frontend` | Веб-интерфейс каталога на Next.js |
| `backend` | REST API на FastAPI |
| `postgres` | Хранение данных о товарах |
| `minio` | Объектное хранилище изображений, совместимое с S3 API |
| `bot` | Telegram-бот для взаимодействия с каталогом и добавления товаров |

Frontend обращается к backend через внутреннюю сеть Docker Compose. Backend использует PostgreSQL для хранения данных и MinIO для работы с изображениями. Telegram-бот взаимодействует с backend по внутреннему адресу.

## Технологии

- Python
- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL
- MinIO / S3 API
- boto3
- Telegram Bot API
- Next.js
- React
- TypeScript
- Docker Compose

## Требования

Для локального запуска необходимы:

- Docker Engine и Docker Compose.
- Telegram-бот, созданный через [@BotFather](https://t.me/BotFather), если требуется проверить интеграцию с Telegram.
- Доступ к Telegram для проверки работы бота.

## Настройка окружения

### 1. Создание конфигурационных файлов

Из корня репозитория выполни:

```bash
cp .env.example .env
cp bot/.env.example bot/.env
```

Открой `.env` и `bot/.env` и замени шаблонные значения собственными.

В корневом `.env` задаются:

- `POSTGRES_DB` — имя базы данных.
- `POSTGRES_USER` — пользователь PostgreSQL.
- `POSTGRES_PASSWORD` — пароль PostgreSQL.
- `MINIO_ROOT_USER` — имя администратора MinIO.
- `MINIO_ROOT_PASSWORD` — пароль администратора MinIO.
- `DATABASE_URL` — строка подключения к PostgreSQL для локального запуска вне Docker.

В `bot/.env` задаются:

- `BOT_TOKEN` — токен Telegram-бота.
- `ADMIN_IDS` — Telegram ID администраторов.
- `API_BASE_URL` — адрес backend для бота.
- `WEB_APP_URL` — публичный HTTPS-адрес веб-каталога.

При запуске через Docker Compose адреса сервисов используются во внутренней сети Compose. В частности, Compose задаёт backend URL для frontend и бота самостоятельно.

## Запуск проекта

Все команды ниже выполняются из корня репозитория.

### 1. Запуск PostgreSQL и MinIO

```bash
docker compose up -d postgres minio
```

Проверка состояния сервисов:

```bash
docker compose ps
```

PostgreSQL и MinIO должны пройти проверки готовности.

### 2. Создание бакета MinIO

Backend использует бакет `product-images` по умолчанию. Код приложения обращается к нему, но автоматически не создаёт его.

Создай бакет с помощью временного контейнера `minio/mc`:

```bash
docker run --rm \
  --network test-catalog_default \
  --env MINIO_ROOT_USER \
  --env MINIO_ROOT_PASSWORD \
  --entrypoint /bin/sh \
  minio/mc:latest -c '
    mc alias set local http://minio:9000 \
      "$MINIO_ROOT_USER" "$MINIO_ROOT_PASSWORD" &&
    mc mb --ignore-existing local/product-images
  '
```

Перед выполнением команды переменные `MINIO_ROOT_USER` и `MINIO_ROOT_PASSWORD` должны быть экспортированы в текущей оболочке и соответствовать значениям из `.env`. Файл `.env` сам по себе не экспортирует переменные в оболочку.

Например, можно открыть отдельную оболочку с экспортом переменных из `.env`, не выводя значения на экран:

```bash
set -a
source .env
set +a
```

После этого выполни команду создания бакета в той же оболочке.

Команда использует имя сети `test-catalog_default`, соответствующее текущему Compose-проекту. Если проект запускается под другим именем, проверь фактическое имя сети:

```bash
docker network ls
```

### 3. Сборка и запуск backend

```bash
docker compose up -d --build backend
```

Backend ожидает готовности PostgreSQL и MinIO.

### 4. Применение миграций базы данных

Миграции выполняются вручную:

```bash
docker compose exec backend alembic upgrade head
```

Команда приводит схему базы данных к последней доступной ревизии Alembic.

### 5. Запуск frontend и Telegram-бота

```bash
docker compose up -d --build frontend bot
```

Для сборки и запуска всех сервисов одной командой также можно использовать:

```bash
docker compose up -d --build
```

При первом запуске не забудь предварительно создать бакет MinIO и применить миграции.

## Локальные адреса

При стандартной конфигурации Compose доступны следующие адреса:

| Компонент | Адрес |
|---|---|
| Веб-каталог | http://127.0.0.1:3000 |
| Backend API | http://127.0.0.1:8010 |
| Проверка backend | http://127.0.0.1:8010/health |
| Документация FastAPI | http://127.0.0.1:8010/docs |
| Консоль MinIO | http://127.0.0.1:9001 |
| S3 API MinIO | http://127.0.0.1:9000 |

Порты опубликованы на loopback-интерфейсе хоста и предназначены для локальной разработки.

## REST API

| Метод | Endpoint | Назначение |
|---|---|---|
| `GET` | `/health` | Проверка состояния backend |
| `GET` | `/products` | Получение списка товаров |
| `GET` | `/products/{product_id}` | Получение товара по ID |
| `POST` | `/products` | Создание товара без изображения |
| `GET` | `/products/{product_id}/image` | Получение изображения товара |
| `POST` | `/products/with-image` | Создание товара с изображением |

Для создания товара с изображением используется форма с названием товара и файлом изображения. Поддерживаемые типы изображений и ограничения размера проверяются backend.

Интерактивная документация API доступна по адресу `http://127.0.0.1:8010/docs`.

## Проверка работоспособности

Проверить состояние контейнеров:

```bash
docker compose ps
```

Проверить backend:

```bash
curl -fsS http://127.0.0.1:8010/health
```

Получить список товаров:

```bash
curl -fsS http://127.0.0.1:8010/products
```

Проверить frontend:

```bash
curl -I http://127.0.0.1:3000/
```

Ожидаемый результат для health endpoint — JSON с полем `status` и значением `good`. Для остальных запросов ориентируйся на HTTP-статус и содержимое ответа.

## Telegram-бот

Бот доступен по ссылке: [@test_product_catalog_bot](https://t.me/test_product_catalog_bot).

Для проверки интеграции:

1. Настрой `BOT_TOKEN` и `ADMIN_IDS` в `bot/.env`.
2. Укажи в `WEB_APP_URL` публичный HTTPS-адрес веб-каталога.
3. Запусти контейнер бота.
4. Отправь боту команду `/start`.
5. Открой каталог через кнопку веб-приложения.
6. Для административного аккаунта проверь добавление товара по инструкции, которую бот показывает после `/start`.

Административные возможности доступны только Telegram ID, указанным в `ADMIN_IDS`. Токен бота не должен попадать в репозиторий.

Telegram Mini App требует доступного по HTTPS веб-адреса. Локальный адрес `http://127.0.0.1:3000` для этого не подходит.

## Остановка

Остановить сервисы, сохранив данные в именованных томах:

```bash
docker compose down
```

Удаление контейнеров и томов с данными — отдельная операция. Не используй `docker compose down -v`, если необходимо сохранить данные PostgreSQL и MinIO.

## Демонстрация

Проект создан в рамках тестового задания и демонстрирует реализацию каталога товаров с интеграцией Telegram-бота и объектного хранилища MinIO.

- GitHub: [sega211/test-product-catalog](https://github.com/sega211/test-product-catalog)
- Telegram: [@test_product_catalog_bot](https://t.me/test_product_catalog_bot)
- Публичный каталог: [catalog.mnogodeto4ka.ru](https://catalog.mnogodeto4ka.ru) — доступность зависит от текущего состояния развёртывания.

Представленные товары и изображения используются в демонстрационных целях.
