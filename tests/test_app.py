from http import HTTPStatus


def test_read_root_deve_retornar_ok_e_ola_mundo(client):
    response = client.get("/")  # Act (AÇÃO)
    assert response.status_code == HTTPStatus.OK  # Assert (AFIRMAÇÃO)
    assert response.json() == {"message": "Olá mundo"}  # Assert (AFIRMAÇÃO)


def test_create_user_deve_retornar_created_e_usuario_criado(client):
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


def test_read_users_deve_retornar_ok_e_lista_de_usuarios(client):
    response = client.get("/users/")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "users": [
            {
                "id": 1,
                "username": "fulano",
                "email": "email@example.com",
            }
        ]
    }


def test_read_user_deve_retornar_ok_e_usuario_deletado(client):
    response = client.get("/users/1/")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "id": 1,
        "username": "fulano",
        "email": "email@example.com",
    }


def test_read_user_deve_retornar_not_found_quando_usuario_nao_existe(client):
    response = client.get("/users/2/")
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_update_user_deve_retornar_ok_e_usuario_atualizado(client):
    response = client.put(
        "/users/1/",
        json={
            "username": "beltrano",
            "email": "beltrano@example.com",
            "password": "123456"
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "id": 1,
        "username": "beltrano",
        "email": "beltrano@example.com"
    }


def test_update_user_deve_retornar_not_found_quando_usuario_nao_existe(client):
    response = client.put(
        "/users/2/",
        json={
            "username": "beltrano",
            "email": "beltrano@example.com",
            "password": "123456"
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_delete_user_deve_retornar_ok_e_usuario_deletado(client):
    response = client.delete("/users/1/")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"message": "User deleted"}


def test_delete_user_deve_retornar_not_found_quando_usuario_nao_existe(client):
    response = client.delete("/users/2/")
    assert response.status_code == HTTPStatus.NOT_FOUND
