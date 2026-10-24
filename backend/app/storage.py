from functools import lru_cache
from io import BytesIO
import boto3
from botocore.client import BaseClient
from botocore.config import Config
from app.config import settings

@lru_cache(maxsize=1)
def get_storage_client() -> BaseClient:
    return boto3.client(
        "s3",
        endpoint_url=settings.minio_endpoint,
        aws_access_key_id=settings.minio_root_user,
        aws_secret_access_key=settings.minio_root_password,
        config =Config(signature_version="s3v4"),
        region_name="us-east-1"
    )

def upload_image(
    image_key: str,
    content: bytes,
    content_type: str
 ) -> None:
    get_storage_client().put_object(
        Bucket=settings.minio_bucket,
        Key=image_key,
        Body=BytesIO(content),
        ContentType=content_type
    )

def read_image(image_key: str) -> tuple[bytes, str]:
    response = get_storage_client().get_object(
        Bucket=settings.minio_bucket,
        Key=image_key
    )

    try:
        content = response["Body"].read()
        content_type = response.get("ContentType", "application/octet-stream")
        return content, content_type
    finally:
        response["Body"].close()

def delete_image(image_key: str) -> None:
    get_storage_client().delete_object(
        Bucket=settings.minio_bucket,
        Key=image_key
    )
