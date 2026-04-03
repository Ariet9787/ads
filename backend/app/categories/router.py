from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.auth.dependencies import get_current_admin_user
from . import schemas
from . import service

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post(
    "/", response_model=schemas.CategoryResponse, status_code=status.HTTP_201_CREATED
)
async def create_category(
    category: schemas.CategoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_admin_user),
):
    try:
        return await service.create_category(db, category)
    except service.CategoryValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except service.CategoryConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.get("/", response_model=list[schemas.CategoryResponse])
async def get_categories(db: AsyncSession = Depends(get_db)):
    return await service.get_categories(db)


@router.get("/{category_id}", response_model=schemas.CategoryResponse)
async def get_category(category_id: int, db: AsyncSession = Depends(get_db)):
    category = await service.get_category(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Категория не найдена")
    return category


@router.put("/{category_id}", response_model=schemas.CategoryResponse)
async def update_category(
    category_id: int,
    data: schemas.CategoryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_admin_user),
):
    try:
        return await service.update_category(db, category_id, data)
    except service.CategoryNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except service.CategoryValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except service.CategoryConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.delete("/{category_id}")
async def delete_category(category_id: int, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_admin_user)):
    try:
        await service.delete_category(db, category_id)
    except service.CategoryNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except service.CategoryConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    return {"status": "удалено"}
