from http import HTTPStatus

from freezegun import freeze_time


def test_get_token(client, user):
    response = client.post(
        "/auth/token",
        data={"username": user.email, "password": user.clean_password},
    )

    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert token["token_type"] == "Bearer"
    assert "access_token" in token


def test_get_token_bad_request(client, user):
    response = client.post(
        "/auth/token",
        data={"username": user.email, "password": "wrongpassword"},
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_token_expired_after_time(client, user):
    with freeze_time("2023-07-14 12:00:00"):
        # Gerar o token as 12:00
        response = client.post(
            "/auth/token",
            data={"username": user.email, "password": user.clean_password},
        )

        token = response.json()

        assert response.status_code == HTTPStatus.OK
        token = token["access_token"]

    with freeze_time("2023-07-14 12:31:01"):
        # Verificar se o token expirou
        response = client.put(
            f"/users/{user.id}/",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "username": "wronguser",
                "email": "wronguser@example.com",
                "password": "123456",
            },
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {"detail": "Could not validate credentials"}


def test_refresh_token(client, token):
    response = client.post(
        "/auth/refresh_token",
        headers={"Authorization": f"Bearer {token}"},
    )

    data = response.json()

    assert response.status_code == HTTPStatus.OK
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "Bearer"


def test_refresh_token_expired_after_time(client, user):
    with freeze_time("2023-07-14 12:00:00"):
        # Gerar o token as 12:00
        response = client.post(
            "/auth/token",
            data={"username": user.email, "password": user.clean_password},
        )

        token = response.json()

        assert response.status_code == HTTPStatus.OK
        token = token["access_token"]

    with freeze_time("2023-07-14 12:31:01"):
        # Verificar se o token expirou
        response = client.post(
            "/auth/refresh_token",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {"detail": "Could not validate credentials"}
