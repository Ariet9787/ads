from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Ad, AdImage
from .schemas import AdCreate, AdUpdate, AdImageCreate
from app.categories.service import _get_category_or_none as get_category
from app.users.models import User


class AdNotFoundError(Exception):
    pass


class AdValidationError(Exception):
    pass


async def _get_ad_or_none(db: AsyncSession, ad_id: int) -> Ad | None:
    result = await db.execute(select(Ad).where(Ad.id == ad_id))
    return result.scalar_one_or_none()


async def create_ad(db: AsyncSession, ad_data: AdCreate, user_id: int) -> Ad:
    # Validate category exists
    category = await get_category(db, ad_data.category_id)
    if not category:
        raise AdValidationError("Категория не найдена")

    ad = Ad(
        title=ad_data.title,
        description=ad_data.description,
        price=ad_data.price,
        category_id=ad_data.category_id,
        user_id=user_id,
    )
    db.add(ad)
    try:
        await db.commit()
        await db.refresh(ad)

        # Add images if provided
        if ad_data.images:
            for image_data in ad_data.images:
                image = AdImage(
                    ad_id=ad.id,
                    url=image_data.url,
                    order=image_data.order,
                )
                db.add(image)
            await db.commit()
            await db.refresh(ad)
    except IntegrityError as exc:
        await db.rollback()
        raise AdValidationError("Ошибка при создании объявления") from exc
    return ad


async def get_ads(
    db: AsyncSession, skip: int = 0, limit: int = 10
) -> tuple[list[Ad], int]:
    # Get total count
    total_result = await db.execute(select(func.count(Ad.id)))
    total = total_result.scalar()

    # Get paginated ads
    result = await db.execute(
        select(Ad).options(selectinload(Ad.images)).offset(skip).limit(limit)
    )
    ads = list(result.scalars().all())
    return ads, total


async def get_ads_by_user(
    db: AsyncSession, user_id: int, skip: int = 0, limit: int = 10
) -> tuple[list[Ad], int]:
    # Get total count for user
    total_result = await db.execute(
        select(func.count(Ad.id)).where(Ad.user_id == user_id)
    )
    total = total_result.scalar()

    # Get paginated ads for user
    result = await db.execute(
        select(Ad)
        .options(selectinload(Ad.images))
        .where(Ad.user_id == user_id)
        .offset(skip)
        .limit(limit)
    )
    ads = list(result.scalars().all())
    return ads, total


async def get_ad(db: AsyncSession, ad_id: int) -> Ad | None:
    result = await db.execute(
        select(Ad).options(selectinload(Ad.images)).where(Ad.id == ad_id)
    )
    return result.scalar_one_or_none()


async def update_ad(
    db: AsyncSession, ad_id: int, ad_data: AdUpdate, user_id: int
) -> Ad:
    ad = await _get_ad_or_none(db, ad_id)
    if not ad:
        raise AdNotFoundError("Объявление не найдено")

    if ad.user_id != user_id:
        raise AdValidationError("Нет прав на редактирование этого объявления")

    if ad_data.category_id is not None:
        category = await get_category(db, ad_data.category_id)
        if not category:
            raise AdValidationError("Категория не найдена")

    for field, value in ad_data.model_dump(exclude_unset=True).items():
        setattr(ad, field, value)

    try:
        await db.commit()
        await db.refresh(ad)
    except IntegrityError as exc:
        await db.rollback()
        raise AdValidationError("Ошибка при обновлении объявления") from exc
    return ad


async def delete_ad(db: AsyncSession, ad_id: int, user_id: int) -> None:
    ad = await _get_ad_or_none(db, ad_id)
    if not ad:
        raise AdNotFoundError("Объявление не найдено")

    if ad.user_id != user_id:
        raise AdValidationError("Нет прав на удаление этого объявления")

    await db.delete(ad)
    await db.commit()


async def add_image_to_ad(
    db: AsyncSession, ad_id: int, image_data: AdImageCreate, user_id: int
) -> AdImage:
    ad = await _get_ad_or_none(db, ad_id)
    if not ad:
        raise AdNotFoundError("Объявление не найдено")

    if ad.user_id != user_id:
        raise AdValidationError("Нет прав на добавление изображений к этому объявлению")

    image = AdImage(
        ad_id=ad_id,
        url=image_data.url,
        order=image_data.order,
    )
    db.add(image)
    try:
        await db.commit()
        await db.refresh(image)
    except IntegrityError as exc:
        await db.rollback()
        raise AdValidationError("Ошибка при добавлении изображения") from exc
    return image


async def remove_image_from_ad(
    db: AsyncSession, ad_id: int, image_id: int, user_id: int
) -> None:
    ad = await _get_ad_or_none(db, ad_id)
    if not ad:
        raise AdNotFoundError("Объявление не найдено")

    if ad.user_id != user_id:
        raise AdValidationError("Нет прав на удаление изображений из этого объявления")

    result = await db.execute(
        select(AdImage).where(AdImage.id == image_id, AdImage.ad_id == ad_id)
    )
    image = result.scalar_one_or_none()
    if not image:
        raise AdNotFoundError("Изображение не найдено")

    await db.delete(image)
    await db.commit()
