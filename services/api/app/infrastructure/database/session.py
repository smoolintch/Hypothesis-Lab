from sqlalchemy import create_engine as sqlalchemy_create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from app.infrastructure.config.settings import get_settings


def create_engine() -> Engine:
    settings = get_settings()
    return sqlalchemy_create_engine(settings.database_url, pool_pre_ping=True)


def create_session_factory() -> sessionmaker:
    engine = create_engine()
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)
