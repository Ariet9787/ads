from typing import Optional, List
from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator


class AdImageBase(BaseModel):
    url: str
    order: Optional[int] = 0


class AdImageCreate(AdImageBase):
    pass


class AdImageResponse(AdImageBase):
    id: int
    ad_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AdBase(BaseModel):
    title: str
    description: str
    price: float
    category_id: int

    @field_validator("price")
    @classmethod
    def validate_price(cls, value):
        if value < 0:
            raise ValueError("Цена не может быть отрицательной")
        return value


class AdCreate(AdBase):
    images: Optional[List[AdImageCreate]] = []


class AdUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category_id: Optional[int] = None

    @field_validator("price")
    @classmethod
    def validate_price(cls, value):
        if value is not None and value < 0:
            raise ValueError("Цена не может быть отрицательной")
        return value


class AdResponse(AdBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    images: List[AdImageResponse] = []

    model_config = ConfigDict(from_attributes=True)


class PaginatedAdResponse(BaseModel):
    items: List[AdResponse]
    total: int
    page: int
    size: int
    pages: int

    model_config = ConfigDict(from_attributes=True)
