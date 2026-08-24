from fastapi import status
from fastapi.testclient import TestClient

from app.main import app


def test_create_channel_integration():
    with TestClient(app) as client:
        response = client.post(
            "/channels",
            json={"name": "integration-test-channel"},
        )

    assert response.status_code == status.HTTP_201_CREATED

    body = response.json()

    assert "data" in body
    assert body["data"]["id"] is not None
    assert body["data"]["name"] == "integration-test-channel"
    assert "createdAt" in body["data"]
