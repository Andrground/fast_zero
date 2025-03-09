from http import HTTPStatus

from fastapi.testclient import TestClient

from fast_zero.app import app


def test_read_root_deve_retornar_ok_e_ola_mundo():
    client = TestClient(app)  # Arrange (ORGANIZAÇÃO)

    response = client.get("/")  # Act (AÇÃO)
    assert response.status_code == HTTPStatus.OK  # Assert (AFIRMAÇÃO)
    assert response.json() == {"message": "Olá mundo"}  # Assert (AFIRMAÇÃO)
