from __future__ import annotations

import contextlib
import os
from collections.abc import AsyncIterator
from functools import lru_cache

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

DEFAULT_DB_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///:memory:")


@lru_cache(maxsize=8)
def get_engine(url: str | None = None, echo: bool = False) -> AsyncEngine:
    engine = create_async_engine(url or DEFAULT_DB_URL, echo=echo, future=True)
    return engine


@lru_cache(maxsize=8)
def get_sessionmaker(
    url: str | None = None, echo: bool = False
) -> async_sessionmaker[AsyncSession]:
    engine = get_engine(url=url, echo=echo)
    return async_sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)


@contextlib.asynccontextmanager
async def get_session(url: str | None = None, echo: bool = False) -> AsyncIterator[AsyncSession]:
    sm = get_sessionmaker(url=url, echo=echo)
    async with sm() as session:
        yield session
