from pydantic import BaseModel, ConfigDict, Field, field_validator

class ProductCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)

    @field_validator('title')
    @classmethod
    def validate_title(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Наименование не должно быть пустым")
        return value

class ProductResponse(BaseModel):
    id: int
    title: str

    model_config = ConfigDict(from_attributes=True)