from app.repositories.channel_repository import ChannelRepository
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


def test_channel_is_persisted_in_database():
    with TestClient(app) as client:
        response = client.post(
            "/channels",
            json={"name": "persistent-channel"},
        )

        assert response.status_code == status.HTTP_201_CREATED

        created_channel = response.json()["data"]

        persisted_channel = ChannelRepository.find_by_name_ci("persistent-channel")

    assert persisted_channel is not None
    assert persisted_channel.id == created_channel["id"]
    assert persisted_channel.name == "persistent-channel"


def test_get_all_channels_integration():
    with TestClient(app) as client:
        client.post("/channels", json={"name": "integration-test-channel-2"})

        response = client.get("/channels")

    assert response.status_code == status.HTTP_200_OK

    body = response.json()

    assert "data" in body
    assert isinstance(body["data"], list)
    assert any(
        channel["name"] == "integration-test-channel-2" for channel in body["data"]
    )
