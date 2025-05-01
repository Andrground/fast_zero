from http import HTTPStatus

from jwt import decode

from fast_zero.security import create_access_token, settings


def test_jwt():
    data = {"sub": "user2@example.com"}

    token = create_access_token(data)

    result = decode(
        token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
    )

    assert result["sub"] == data["sub"]
    assert result["exp"]


def test_delete_invalid_token(client):
    response = client.delete(
        "/users/1/",
        headers={"Authorization": "Bearer invalido"},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {
        "detail": "Could not validate credentials",
    }


def test_token_wrong_password(client, user):
    response = client.post(
        "/auth/token",
        data={"username": user.email, "password": "wrongpassword"},
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {"detail": "Incorrect username or password"}


def test_token_wrong_email(client, user):
    response = client.post(
        "/auth/token",
        data={"username": "email@test.com", "password": user.clean_password},
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {"detail": "Incorrect username or password"}
