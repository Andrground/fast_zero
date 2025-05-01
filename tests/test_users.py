from http import HTTPStatus

from fast_zero.schemas import UserPublic


def test_create_user(client):
    response = client.post(
        "/users/",
        json={
            "username": "fulano",
            "email": "email@example.com",
            "password": "123456",
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        "id": 1,
        "username": "fulano",
        "email": "email@example.com",
    }


# def test_create_user_bad_request_username(client, user):
#     response = client.post(
#         "/users/",
#         json={
#             "username": "fulano",
#             "email": "email@example.com",
#             "password": "123456",
#         },
#     )

#     assert response.status_code == HTTPStatus.BAD_REQUEST
#     assert response.json() == {"detail": "Username already exists"}


# def test_create_user_bad_request_email(client, user):
#     response = client.post(
#         "/users/",
#         json={
#             "username": "fulano2",
#             "email": "email@example.com",
#             "password": "123456",
#         },
#     )

#     assert response.status_code == HTTPStatus.BAD_REQUEST
#     assert response.json() == {"detail": "Email already exists"}


def test_read_users_empty_list(client):
    response = client.get("/users/")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"users": []}


def test_read_users(client, user):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get("/users/")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"users": [user_schema]}


def test_read_user(client, user):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get(f"/users/{user.id}/")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == user_schema


def test_read_user_not_found(client):
    response = client.get("/users/2/")
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_update_user(client, user, token):
    response = client.put(
        f"/users/{user.id}/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "username": "beltrano",
            "email": "beltrano@example.com",
            "password": "123456",
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "id": user.id,
        "username": "beltrano",
        "email": "beltrano@example.com",
    }


def test_update_user_forbidden(client, other_user, token):
    response = client.put(
        f"/users/{other_user.id}/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "username": "beltrano",
            "email": "beltrano@example.com",
            "password": "123456",
        },
    )

    assert response.status_code == HTTPStatus.FORBIDDEN


def test_delete_user(client, user, token):
    response = client.delete(
        f"/users/{user.id}/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"message": "User deleted"}


def test_delete_user_forbidden(client, other_user, token):
    response = client.delete(
        f"/users/{other_user.id}/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == HTTPStatus.FORBIDDEN


def test_update_integrity_error(client, user, other_user, token):
    response_update = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': other_user.username,
            'email': 'bob@example.com',
            'password': 'mynewpassword',
        },
    )

    assert response_update.status_code == HTTPStatus.CONFLICT
    assert response_update.json() == {
        'detail': 'Username or Email already exists'
    }
