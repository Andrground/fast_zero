from contextlib import contextmanager
from datetime import datetime

import factory
import factory.fuzzy
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from fast_zero.app import app
from fast_zero.database import get_session
from fast_zero.models import User, table_registry, Todo
from fast_zero.security import get_password_hash
from fast_zero.models import TodoState


class UserFactory(factory.Factory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"teste{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@teste.com")
    password = factory.LazyAttribute(lambda obj: f"{obj.username}+senha")


class TodoFactory(factory.Factory):
    class Meta:
        model = Todo

    title = factory.Faker("text")
    description = factory.Faker("text")
    state = factory.fuzzy.FuzzyChoice(TodoState)
    user_id = 1


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
    pwd = "123456"

    user = UserFactory(
        password=get_password_hash(pwd),
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    user.clean_password = pwd

    return user


@pytest.fixture
def other_user(session):
    user = UserFactory()

    session.add(user)
    session.commit()
    session.refresh(user)

    return user


@pytest.fixture
def token(client, user):
    response = client.post(
        "/auth/token",
        data={"username": user.email, "password": user.clean_password},
    )

    return response.json()["access_token"]


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
