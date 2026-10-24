from io import BytesIO
from PIL import Image, UnidentifiedImageError

MAX_IMAGE_SIZE = 5 *1024 *1024
ALLOWED_IMAGE_FORMATS = {
    "JPEG": "image/jpeg",
    "PNG" : 'image/png',
    "WEBP": 'image/webp'
}

class ImageValidationError(ValueError):
    """Ошибка валидации изображения!"""

def validate_image(content: bytes) -> str:
    """Проверяет размер и содержимое изображения.

    Возвращает нормализованный MIME-тип.
    """

    if not content:
        raise ImageValidationError("Файл пуст")

    if len(content) > MAX_IMAGE_SIZE:
        raise ImageValidationError("Размер изображения превышает 5 MB")

    try:
        with Image.open(BytesIO(content)) as image:
            image_format = image.format

            if image_format not in ALLOWED_IMAGE_FORMATS:
                raise ImageValidationError(
                    "Вы можете загрузить JPEG, PNG или WebP"
                )
            image.verify()

    except (UnidentifiedImageError, OSError) as exc:
        raise ImageValidationError(
            "Файл не является корректным изображением"
        ) from exc

    return ALLOWED_IMAGE_FORMATS[image_format]
