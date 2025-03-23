from datetime import datetime
from fast_zero.models import User, table_registry

from sqlalchemy import select

from contextlib import contextmanager

from dataclasses import asdict


def test_create_user(session):
    user = User(username='anderground', email="anderground@teste.com", password='senha123')

    session.add(user)
    session.commit()
    
    result = session.scalar(select(User).where(User.email == 'anderground@teste.com'))

    assert result.id == 1


def test_create_user_updated(session, mock_db_time):
    with mock_db_time(model=User) as time:
        new_user = User(
            username='alice', password='secret', email='teste@test'
        )
        session.add(new_user)
        session.commit()

        user = session.scalar(select(User).where(User.username == 'alice'))

    assert asdict(user) == {
        'id': 1,
        'username': 'alice',
        'password': 'secret',
        'email': 'teste@test',
        'created_at': time,
        'updated_at': time,
    }
