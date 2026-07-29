import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

import app.db.session as db_session_module
from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.core.config import settings

# Isolated in-memory SQLite database for deterministic tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db_session_module.engine = engine
db_session_module.SessionLocal = TestingSessionLocal


@pytest.fixture(scope="function", autouse=True)
def default_mock_settings():
    # Force mock providers during automated test suite runs
    old_video = settings.VIDEO_PROVIDER
    old_director = settings.DIRECTOR_PROVIDER
    settings.VIDEO_PROVIDER = "mock"
    settings.DIRECTOR_PROVIDER = "mock"
    yield
    settings.VIDEO_PROVIDER = old_video
    settings.DIRECTOR_PROVIDER = old_director


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
