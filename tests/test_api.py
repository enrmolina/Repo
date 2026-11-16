import os

from fastapi.testclient import TestClient

from api.app import app


client = TestClient(app)


def setup_module() -> None:
    os.environ["API_KEY"] = "clave-de-prueba"


def test_chat_sin_clave_responde_401() -> None:
    response = client.post("/chat", json={"user_id": "u1", "texto": "Hola"})
    assert response.status_code == 401


def test_chat_con_clave_responde_200() -> None:
    response = client.post(
        "/chat",
        headers={"X-API-Key": "clave-de-prueba"},
        json={"user_id": "u1", "texto": "Hola"},
    )
    assert response.status_code == 200
    assert set(response.json()) == {"ruta", "motivo", "respuesta"}
