from tests.conftest import TodoFactory
from fast_zero.models import TodoState
from http import HTTPStatus


def test_create_todo(client, token):
    response = client.post(
        "/todos/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Test Todo",
            "description": "This is a test todo",
            "state": "draft",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "title": "Test Todo",
        "description": "This is a test todo",
        "state": "draft",
        "created_at": response.json()["created_at"],
        "updated_at": response.json()["updated_at"],
    }


def test_list_todos_only_five(session, client, token, user):
    expected_todos = 5
    session.bulk_save_objects(
        TodoFactory.create_batch(expected_todos, user_id=user.id)
    )
    session.commit()

    response = client.get(
        "/todos/",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == HTTPStatus.OK
    assert expected_todos == len(response.json()["todos"])


def test_list_todos_offset_limit(session, client, token, user):
    expected_todos = 2
    session.bulk_save_objects(TodoFactory.create_batch(5, user_id=user.id))
    session.commit()

    response = client.get(
        "/todos/?offset=1&limit=2",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == HTTPStatus.OK
    assert expected_todos == len(response.json()["todos"])


def test_list_todos_filter_title(session, client, token, user):
    expected_todos = 5
    session.bulk_save_objects(
        TodoFactory.create_batch(expected_todos, user_id=user.id, title="Test")
    )
    session.commit()

    response = client.get(
        "/todos/?title=Test",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == HTTPStatus.OK
    assert expected_todos == len(response.json()["todos"])


def test_list_todos_filter_description(session, client, token, user):
    expected_todos = 5
    session.bulk_save_objects(
        TodoFactory.create_batch(
            expected_todos, user_id=user.id, description="description"
        )
    )
    session.commit()

    response = client.get(
        "/todos/?description=desc",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == HTTPStatus.OK
    assert expected_todos == len(response.json()["todos"])


def test_list_todos_filter_state(session, client, token, user):
    expected_todos = 5
    session.bulk_save_objects(
        TodoFactory.create_batch(
            expected_todos, user_id=user.id, state=TodoState.draft
        )
    )
    session.commit()

    response = client.get(
        "/todos/?state=draft",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == HTTPStatus.OK
    assert expected_todos == len(response.json()["todos"])


def test_list_todos_filter_combined(session, client, token, user):
    expected_todos = 5
    session.bulk_save_objects(
        TodoFactory.create_batch(
            expected_todos,
            user_id=user.id,
            title="Test",
            description="description",
            state=TodoState.done,
        )
    )

    session.bulk_save_objects(
        TodoFactory.create_batch(
            expected_todos,
            user_id=user.id,
            title="another",
            description="other",
            state=TodoState.draft,
        )
    )

    session.commit()

    response = client.get(
        "/todos/?title=Test&description=desc&state=done",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == HTTPStatus.OK
    assert expected_todos == len(response.json()["todos"])


def test_delete_todo(client, token, session, user):
    todo = TodoFactory(user_id=user.id)
    session.add(todo)
    session.commit()
    session.refresh(todo)

    response = client.delete(
        f"/todos/{todo.id}/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"message": "Task deleted successfully"}


def test_delete_todo_false(client, user, token, session):
    todo = TodoFactory(user_id=user.id)
    session.add(todo)
    session.commit()
    session.refresh(todo)
    todo_id = todo.id + 1

    response = client.delete(
        f"/todos/{todo_id}/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {"detail": "Task not found"}


def test_patch_todo(client, token, session, user):
    todo = TodoFactory(user_id=user.id)
    session.add(todo)
    session.commit()
    session.refresh(todo)

    response = client.patch(
        f"/todos/{todo.id}/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "state": "done",
        },
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json()["state"] == "done"


def test_patch_todo_false(client, user, token, session):
    todo = TodoFactory(user_id=user.id)
    session.add(todo)
    session.commit()
    session.refresh(todo)
    todo_id = todo.id + 1

    response = client.patch(
        f"/todos/{todo_id}/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "state": "done",
        },
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {"detail": "Task not found"}
