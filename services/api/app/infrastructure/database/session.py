from collections.abc import Generator
from functools import lru_cache

from sqlalchemy import create_engine as sqlalchemy_create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.infrastructure.config.settings import get_settings


def _connect_args(database_url: str) -> dict[str, object]:
    if database_url.startswith("sqlite"):
        return {"check_same_thread": False}
    return {}


@lru_cache
def create_engine() -> Engine:
    settings = get_settings()
    return sqlalchemy_create_engine(
        settings.database_url,
        pool_pre_ping=True,
        connect_args=_connect_args(settings.database_url),
    )


@lru_cache
def create_session_factory() -> sessionmaker:
    engine = create_engine()
    return sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
        class_=Session,
    )


def get_session() -> Generator[Session, None, None]:
    session_factory = create_session_factory()
    session = session_factory()
    try:
        yield session
    finally:
        session.close()
