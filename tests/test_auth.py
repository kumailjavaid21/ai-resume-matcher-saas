import uuid

from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_signup_and_login_flow():
    unique_email = f"test+{uuid.uuid4().hex[:6]}@example.com"
    response = client.post("/auth/signup", json={"email": unique_email, "password": "secret"})
    assert response.status_code == 200
    assert "access_token" in response.json()

    login_response = client.post("/auth/login", json={"email": unique_email, "password": "secret"})
    assert login_response.status_code == 200
    assert login_response.json()["access_token"]
