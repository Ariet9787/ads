from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.users.models import User
from . import schemas
from . import service

router = APIRouter(prefix="/ads", tags=["ads"])


@router.post(
    "/", response_model=schemas.AdResponse, status_code=status.HTTP_201_CREATED
)
async def create_ad(
    ad: schemas.AdCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return await service.create_ad(db, ad, current_user.id)
    except service.AdValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/", response_model=schemas.PaginatedAdResponse)
async def get_ads(page: int = 1, size: int = 10, db: AsyncSession = Depends(get_db)):
    if page < 1:
        raise HTTPException(
            status_code=400, detail="Номер страницы должен быть больше 0"
        )
    if size < 1 or size > 100:
        raise HTTPException(
            status_code=400, detail="Размер страницы должен быть от 1 до 100"
        )

    skip = (page - 1) * size
    ads, total = await service.get_ads(db, skip, size)
    pages = (total + size - 1) // size  # Ceiling division

    return schemas.PaginatedAdResponse(
        items=[schemas.AdResponse.model_validate(ad) for ad in ads],
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@router.get("/my", response_model=schemas.PaginatedAdResponse)
async def get_my_ads(
    page: int = 1,
    size: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if page < 1:
        raise HTTPException(
            status_code=400, detail="Номер страницы должен быть больше 0"
        )
    if size < 1 or size > 100:
        raise HTTPException(
            status_code=400, detail="Размер страницы должен быть от 1 до 100"
        )

    skip = (page - 1) * size
    ads, total = await service.get_ads_by_user(db, current_user.id, skip, size)
    pages = (total + size - 1) // size  # Ceiling division

    return schemas.PaginatedAdResponse(
        items=[schemas.AdResponse.model_validate(ad) for ad in ads],
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@router.get("/{ad_id}", response_model=schemas.AdResponse)
async def get_ad(ad_id: int, db: AsyncSession = Depends(get_db)):
    ad = await service.get_ad(db, ad_id)
    if not ad:
        raise HTTPException(status_code=404, detail="Объявление не найдено")
    return ad


@router.put("/{ad_id}", response_model=schemas.AdResponse)
async def update_ad(
    ad_id: int,
    data: schemas.AdUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return await service.update_ad(db, ad_id, data, current_user.id)
    except service.AdNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except service.AdValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.delete("/{ad_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ad(
    ad_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        await service.delete_ad(db, ad_id, current_user.id)
    except service.AdNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except service.AdValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post(
    "/{ad_id}/images",
    response_model=schemas.AdImageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_image_to_ad(
    ad_id: int,
    image: schemas.AdImageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return await service.add_image_to_ad(db, ad_id, image, current_user.id)
    except service.AdNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except service.AdValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.delete("/{ad_id}/images/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_image_from_ad(
    ad_id: int,
    image_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        await service.remove_image_from_ad(db, ad_id, image_id, current_user.id)
    except service.AdNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except service.AdValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
