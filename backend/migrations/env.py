import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import (
    create_async_engine,
)  # Важно: используем асинхронный движок

from alembic import context


# 1. Импорты вашего проекта
from app.database import Base, DATABASE_URL
from app.users.models import User
from app.categories.models import Category
from app.ads.models import Ad
from app.ads.models import AdImage


# Объект конфигурации Alembic
config = context.config


# Настройка логирования
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Указываем метаданные ваших моделей
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Оффлайн режим (генерация SQL скриптов)"""
    url = DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """Вспомогательная функция для запуска миграций в синхронном контексте внутри асинхронного"""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Онлайн режим (асинхронное подключение к БД)"""
    # Создаем асинхронный движок напрямую из вашего DATABASE_URL
    connectable = create_async_engine(
        DATABASE_URL,
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        # Alembic работает синхронно, поэтому используем run_sync
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    # Запускаем асинхронную функцию в цикле событий
    asyncio.run(run_migrations_online())
