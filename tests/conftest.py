from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app import models  # noqa: F401
from app.core.config import Settings, get_settings
from app.dependencies.database import Base, get_db
from app.main import app

API_KEY = "test-api-key"


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)

    session = sessionmaker(
        bind=engine,
        autoflush=False,
        expire_on_commit=False,
    )()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)
        engine.dispose()


@pytest.fixture
def anonymous_client(
    db_session: Session,
) -> Generator[TestClient, None, None]:
    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[get_settings] = lambda: Settings(
        _env_file=None,
        api_key=API_KEY,
    )

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def client(
    anonymous_client: TestClient,
) -> TestClient:
    return TestClient(app, headers={"X-API-Key": API_KEY})