from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str

    minio_endpoint: str = "http://127.0.0.1:9000"
    minio_root_user: str
    minio_root_password: str
    minio_bucket: str = "product-images"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

settings=Settings()