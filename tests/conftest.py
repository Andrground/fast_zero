import pytest
from fastapi.testclient import TestClient

from fast_zero.app import app
from fast_zero.models import table_registry, User

from sqlalchemy import create_engine, event
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import Session

from contextlib import contextmanager
from datetime import datetime

from fast_zero.database import get_session


@pytest.fixture
def client(session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override

        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    table_registry.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    table_registry.metadata.drop_all(engine)


@pytest.fixture
def user(session):
    user = User(
        username="fulano", email="email@example.com", password="123456"
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    return user


@pytest.fixture
def mock_db_time():
    return _mock_db_time


@contextmanager
def _mock_db_time(*, model, time=datetime(2024, 1, 1)):
    def fake_time_handler(mapper, connection, target):
        if hasattr(target, "created_at"):
            target.created_at = time
        if hasattr(target, "updated_at"):
            target.updated_at = time

    event.listen(model, "before_insert", fake_time_handler)

    yield time

    event.remove(model, "before_insert", fake_time_handler)
