from aiogram import Bot, F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    WebAppInfo,
)

from app.config import Settings

router = Router()

MAX_IMAGE_SIZE = 5 * 1024 * 1024
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}


class AddProductStates(StatesGroup):
    waiting_for_title = State()
    waiting_for_photo = State()


@router.message(CommandStart())
async def cmd_start(message: Message, settings: Settings) -> None:
    user_id = message.from_user.id if message.from_user else None

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Открыть каталог",
                    web_app=WebAppInfo(url=settings.web_app_url),
                )
            ]
        ]
    )

    if user_id not in settings.admin_ids:
        await message.answer(
            "У меня есть товар",
            reply_markup=keyboard,
        )
        return

    await message.answer(
        "Здравствуйте! Вы вошли в панель управления каталогом.\n\n"
        "Чтобы добавить товар, отправьте команду /add или нажмите скрепку",
        reply_markup=keyboard,
    )


@router.message(Command("add"))
async def cmd_add(message: Message, state: FSMContext, settings: Settings) -> None:
    user_id = message.from_user.id if message.from_user else None

    if user_id not in settings.admin_ids:
        await message.answer("У вас нет доступа к этой команде.")
        return

    await state.set_state(AddProductStates.waiting_for_title)
    await message.answer(
        "Введите название товара (от 1 до 255 символов).\n"
        "Для отмены отправьте /cancel."
    )


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Добавление товара отменено.")


@router.message(AddProductStates.waiting_for_title, F.text)
async def receive_title(
    message: Message,
    state: FSMContext,
) -> None:
    title = message.text.strip()

    if title.startswith("/"):
        await message.answer(
            "Введите название товара или отправьте /cancel для отмены."
        )
        return

    if not title or len(title) > 255:
        await message.answer(
            "Название должно содержать от 1 до 255 символов. Попробуйте ещё раз."
        )
        return

    await state.update_data(title=title)
    await state.set_state(AddProductStates.waiting_for_photo)
    await message.answer(
        "Теперь отправьте фотографию товара.\n"
        "Поддерживаются JPEG, PNG и WebP размером до 5 MiB."
    )


@router.message(AddProductStates.waiting_for_title, ~F.photo)
async def invalid_title_message(message: Message) -> None:
    await message.answer("Пожалуйста, отправьте название товара текстом.")


@router.message(F.photo)
async def receive_product_photo(
    message: Message,
    settings: Settings,
    bot: Bot,
) -> None:
    import httpx

    user_id = message.from_user.id if message.from_user else None
    if user_id not in settings.admin_ids:
        await message.answer("У вас нет доступа к добавлению товаров.")
        return

    title = (message.caption or "").strip()
    if not title:
        await message.answer(
            "Чтобы добавить товар, отправьте фотографию с названием "
            "в подписи к сообщению."
        )
        return

    if len(title) > 255:
        await message.answer("Название товара не должно превышать 255 символов.")
        return

    photo = message.photo[-1]
    if photo.file_size and photo.file_size > MAX_IMAGE_SIZE:
        await message.answer(
            "Размер фотографии превышает 5 MiB. Отправьте изображение меньшего размера."
        )
        return

    await message.answer("Сохраняю товар…")

    try:
        telegram_file = await bot.get_file(photo.file_id)
        if not telegram_file.file_path:
            await message.answer("Не удалось получить фотографию. Попробуйте ещё раз.")
            return

        from io import BytesIO

        image_buffer = BytesIO()
        await bot.download_file(
            telegram_file.file_path,
            destination=image_buffer,
        )
        image_content = image_buffer.getvalue()

        if not image_content:
            await message.answer("Получен пустой файл. Отправьте фотографию ещё раз.")
            return

        if len(image_content) > MAX_IMAGE_SIZE:
            await message.answer(
                "Размер фотографии превышает 5 MiB. Отправьте изображение меньшего размера."
            )
            return

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{settings.api_base_url}/products/with-image",
                data={"title": title},
                files={
                    "image": (
                        telegram_file.file_path.rsplit("/", 1)[-1],
                        image_content,
                        "application/octet-stream",
                    )
                },
            )

        if response.status_code == 201:
            product = response.json()
            if not isinstance(product, dict) or not {
                "id", "title"
            }.issubset(product):
                await message.answer(
                    "Сервер сохранил товар, но вернул неожиданный ответ. "
                    "Проверьте каталог перед повторной отправкой."
                )
                return

            await message.answer(
                "Товар успешно добавлен!\n\n"
                f"ID: {product['id']}\n"
                f"Название: {product['title']}"
            )
            return

        if response.status_code == 422:
            try:
                detail = response.json().get(
                    "detail",
                    "Проверьте название и фотографию.",
                )
            except ValueError:
                detail = "Проверьте название и фотографию."

            await message.answer(f"Не удалось добавить товар: {detail}")
            return

        await message.answer(
            f"Не удалось сохранить товар (HTTP {response.status_code}). "
            "Попробуйте позже."
        )

    except httpx.HTTPError:
        await message.answer(
            "Не удалось связаться с сервером каталога. Попробуйте позже."
        )
    except (KeyError, ValueError):
        await message.answer(
            "Сервер вернул неожиданный ответ. Попробуйте позже."
        )


@router.message(AddProductStates.waiting_for_photo)
async def invalid_photo_message(message: Message) -> None:
    await message.answer(
        "Пожалуйста, отправьте фотографию как изображение, а не документом."
    )
