from pydantic import BaseModel, field_validator


class Button(BaseModel):
    text: str
    callback: str

    @field_validator('callback')
    def validate_byte_size(cls, v: str) -> str:
        byte_size = len(v.encode('utf-8'))
        if byte_size > 64:
            raise ValueError(
                f"Размер поля превышает 64 байта (текущий размер: {byte_size} байт)"
            )
        return v
