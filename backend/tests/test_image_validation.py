
from io import BytesIO

import pytest
from PIL import Image

from app.image_validation import (
    MAX_IMAGE_SIZE,
    ImageValidationError,
    validate_image,
)


def make_image(image_format: str = "PNG") -> bytes:
    buffer = BytesIO()
    Image.new("RGB", (2, 2), color="red").save(
        buffer,
        format=image_format,
    )
    return buffer.getvalue()


@pytest.mark.parametrize(
    ("image_format", "expected_content_type"),
    [
        ("JPEG", "image/jpeg"),
        ("PNG", "image/png"),
        ("WEBP", "image/webp"),
    ],
)
def test_validate_image_accepts_supported_formats(
    image_format: str,
    expected_content_type: str,
):
    content = make_image(image_format)

    assert validate_image(content) == expected_content_type


def test_validate_image_rejects_empty_content():
    with pytest.raises(ImageValidationError, match="Файл пуст"):
        validate_image(b"")


def test_validate_image_rejects_invalid_content():
    with pytest.raises(
        ImageValidationError,
        match="не является корректным изображением",
    ):
        validate_image(b"not an image")


def test_validate_image_rejects_unsupported_format():
    content = make_image("GIF")

    with pytest.raises(
        ImageValidationError,
        match="Вы можете загрузить JPEG, PNG или WebP",
    ):
        validate_image(content)


def test_validate_image_rejects_content_over_size_limit():
    content = b"x" * (MAX_IMAGE_SIZE + 1)

    with pytest.raises(
        ImageValidationError,
        match="Размер изображения превышает 5 MB",
    ):
        validate_image(content)
