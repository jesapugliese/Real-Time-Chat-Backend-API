from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch
from app.services.channel_service import ChannelService
from app.models.channel import Channel
from datetime import datetime
from fastapi import status
from app.api.errors.channel import ChannelAlreadyExistsError, InvalidChannelNameError


client = TestClient(app)


def assert_error_format(body):
    """
    Asserts that the error response follows the RFC 7807 Problem
    Details format.
    """

    assert body["type"] == "about:blank"
    assert "title" in body
    assert body["status"] == status.HTTP_400_BAD_REQUEST
    assert "detail" in body
    assert "instance" in body


def test_create_channel_success():
    with patch.object(
        ChannelService,
        "create_channel",
        return_value=Channel(
            id=1, name="Test Channel", createdAt=datetime(2026, 8, 23, 18, 0, 0)
        ),
    ):
        response = client.post("/channels", json={"name": "Test Channel"})

    assert response.status_code == status.HTTP_201_CREATED

    body = response.json()

    assert body["data"]["name"] == "Test Channel"


def test_create_channel_empty_name():
    response = client.post("/channels", json={"name": ""})

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    body = response.json()
    assert_error_format(body)


def test_create_channel_too_long_name():
    long_name = "A" * 51
    response = client.post("/channels", json={"name": long_name})

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    body = response.json()
    assert_error_format(body)


def test_create_channel_already_exists():
    with patch.object(
        ChannelService,
        "create_channel",
        side_effect=ChannelAlreadyExistsError("Test Channel"),
    ):
        response = client.post("/channels", json={"name": "Test Channel"})

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    body = response.json()
    assert_error_format(body)


def test_list_channels_success():
    with patch.object(
        ChannelService,
        "get_all_channels",
        return_value=[
            Channel(id=1, name="Channel 1", createdAt=datetime(2026, 8, 23, 18, 0, 0)),
            Channel(id=2, name="Channel 2", createdAt=datetime(2026, 8, 23, 18, 5, 0)),
        ],
    ):
        response = client.get("/channels")

    assert response.status_code == status.HTTP_200_OK

    body = response.json()

    assert len(body["data"]) == 2
    assert body["data"][0]["name"] == "Channel 1"
    assert body["data"][1]["name"] == "Channel 2"


def test_list_channels_empty():
    with patch.object(ChannelService, "get_all_channels", return_value=[]):
        response = client.get("/channels")

    assert response.status_code == status.HTTP_200_OK

    body = response.json()

    assert len(body["data"]) == 0
