from jwt import decode
from fast_zero.security import create_access_token, SECRET_KEY, ALGORITHM
from http import HTTPStatus


def test_jwt():
    data = {"sub": "user2@example.com"}

    token = create_access_token(data)

    result = decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    assert result["sub"] == data["sub"]
    assert result["exp"]


def test_delete_invalid_token(client):
    response = client.delete( 
        "/users/1/",
        headers={"Authorization": f"Bearer invalido"},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {
        "detail": "Could not validate credentials",
    }
