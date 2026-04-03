from pydantic import BaseModel, EmailStr, Field, field_validator
import re


class UserCreate(BaseModel):
    email: EmailStr

    username: str = Field(
        min_length=3,
        max_length=10,
        description="Имя пользователя, может содержать только буквы, цифры и от 3 до 10 символов",
    )

    phone: str = Field(
        min_length=10,
        max_length=15,
        description="Номер телефона, может содержать только цифры и опциональный + в начале",
    )

    password: str = Field(
        min_length=8,
        max_length=128,
        description="Пароль должен содержать минимум 8 символов",
    )

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str):
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError(
                "Имя пользователя может содержать только буквы, цифры и подчеркивания"
            )
        return v

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str):
        if not re.match(r"^\+?\d+$", v):
            raise ValueError(
                "Номер телефона должен содержать только цифры и опциональный + в начале"
            )
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str):
        if not re.search(r"[A-Z]", v):
            raise ValueError("Пароль должен содержать хотя бы одну заглавную букву")
        if not re.search(r"[a-z]", v):
            raise ValueError("Пароль должен содержать хотя бы одну строчную букву")
        if not re.search(r"\d", v):
            raise ValueError("Пароль должен содержать хотя бы одну цифру")
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class Token(BaseModel):
    access_token: str
    token_type: str
