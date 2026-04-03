from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from slugify import slugify

from .models import Category
from .schemas import CategoryCreate, CategoryUpdate


class CategoryNotFoundError(Exception):
    pass


class CategoryConflictError(Exception):
    pass


class CategoryValidationError(Exception):
    pass


async def _get_category_or_none(db: AsyncSession, category_id: int) -> Category | None:
    result = await db.execute(select(Category).where(Category.id == category_id))
    return result.scalar_one_or_none()


async def _validate_parent_id(
    db: AsyncSession,
    parent_id: int | None,
    current_category_id: int | None = None,
) -> None:
    if parent_id is None:
        return

    if current_category_id is not None and parent_id == current_category_id:
        raise CategoryValidationError("Категория не может быть родителем самой себя")

    parent = await _get_category_or_none(db, parent_id)
    if not parent:
        raise CategoryValidationError("Родительская категория не найдена")

    # Prevent cycles by walking up parent chain.
    seen: set[int] = set()
    cursor = parent
    while cursor.parent_id is not None:
        if current_category_id is not None and cursor.parent_id == current_category_id:
            raise CategoryValidationError("Нельзя создать циклическую иерархию категорий")

        if cursor.parent_id in seen:
            break
        seen.add(cursor.parent_id)

        cursor = await _get_category_or_none(db, cursor.parent_id)
        if not cursor:
            break


async def create_category(db: AsyncSession, data: CategoryCreate) -> Category:
    await _validate_parent_id(db, data.parent_id)

    category = Category(
        name=data.name,
        slug=slugify(data.name),
        parent_id=data.parent_id,
    )

    try:
        db.add(category)
        await db.commit()
        await db.refresh(category)
    except IntegrityError as exc:
        await db.rollback()
        raise CategoryConflictError("Категория с таким slug уже существует") from exc

    return category


async def get_categories(db: AsyncSession) -> list[Category]:
    result = await db.execute(select(Category).order_by(Category.id))
    return list(result.scalars().all())


async def get_category(db: AsyncSession, category_id: int) -> Category | None:
    return await _get_category_or_none(db, category_id)


async def update_category(
    db: AsyncSession,
    category_id: int,
    data: CategoryUpdate,
) -> Category:
    category = await _get_category_or_none(db, category_id)
    if not category:
        raise CategoryNotFoundError("Категория не найдена")

    payload = data.model_dump(exclude_unset=True)

    if "name" in payload and payload["name"] is not None:
        category.name = payload["name"]
        category.slug = slugify(payload["name"])

    if "parent_id" in payload:
        await _validate_parent_id(db, payload["parent_id"], current_category_id=category_id)
        category.parent_id = payload["parent_id"]

    try:
        await db.commit()
        await db.refresh(category)
    except IntegrityError as exc:
        await db.rollback()
        raise CategoryConflictError("Категория с таким slug уже существует") from exc

    return category


async def delete_category(db: AsyncSession, category_id: int) -> bool:
    category = await _get_category_or_none(db, category_id)
    if not category:
        raise CategoryNotFoundError("Категория не найдена")

    try:
        await db.delete(category)
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise CategoryConflictError(
            "Нельзя удалить категорию: есть связанные записи"
        ) from exc

    return True
