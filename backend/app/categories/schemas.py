from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator


class CategoryBase(BaseModel):
    name: str
    parent_id: Optional[int] = None

    @field_validator("parent_id", mode="before")
    @classmethod
    def normalize_parent_id(cls, value):
        if value in ("", 0, "0"):
            return None
        if value is not None and int(value) < 0:
            raise ValueError("parent_id не может быть отрицательным")
        return value


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    parent_id: Optional[int] = None

    @field_validator("parent_id", mode="before")
    @classmethod
    def normalize_parent_id(cls, value):
        if value in ("", 0, "0"):
            return None
        if value is not None and int(value) < 0:
            raise ValueError("parent_id не может быть отрицательным")
        return value


class CategoryResponse(CategoryBase):
    id: int
    slug: str

    model_config = ConfigDict(from_attributes=True)
