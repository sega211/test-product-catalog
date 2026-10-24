# Каталог товаров — Frontend

Frontend каталога товаров на Next.js 16 с App Router. Приложение получает список товаров и изображения через собственные API-маршруты Next.js, которые проксируют запросы к FastAPI backend.

## Технологии

- Next.js 16
- React 19
- TypeScript
- ESLint
- Docker

## Локальная разработка

Из корня репозитория:

```bash
cd frontend
npm ci
npm run dev
```

Откройте http://localhost:3000.

Для работы каталога backend должен быть доступен по адресу `http://127.0.0.1:8010`.

## Проверки

```bash
npx tsc --noEmit
npm run lint
npm run build
```

## Запуск через Docker Compose

Из корня репозитория:

```bash
docker compose build frontend
docker compose up -d frontend
```

Frontend будет доступен по адресу http://localhost:3000.

Внутри Docker frontend обращается к backend по адресу `http://backend:8010`, заданному переменной окружения `BACKEND_URL`.

## API-маршруты frontend

- `GET /api/products` — получить список товаров.
- `GET /api/products/{id}/image` — получить изображение товара.

Изображения передаются через Next.js API-маршрут, а не загружаются браузером напрямую из MinIO.
