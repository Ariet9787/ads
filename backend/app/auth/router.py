# app/auth/router.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.users.models import User
from app.auth.schemas import UserCreate, UserLogin, Token
from app.auth.security import hash_password, verify_password
from app.auth.jwt import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):

    stmt = select(User).where(User.email == user.email)
    result = await db.execute(stmt)
    exists = result.scalar_one_or_none()

    if exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    new_user = User(
        email=user.email,
        username=user.username,
        phone=user.phone,
        hashed_password=hash_password(user.password),
    )

    try:
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
    except Exception:
        await db.rollback()
        raise

    access_token = create_access_token({"sub": str(new_user.id)})

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.post("/login", response_model=Token)
async def login(user: UserLogin, db: AsyncSession = Depends(get_db)):

    stmt = select(User).where(User.email == user.email)
    result = await db.execute(stmt)
    db_user = result.scalar_one_or_none()

    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token({"sub": str(db_user.id)})

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }
