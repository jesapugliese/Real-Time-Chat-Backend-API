from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch
from app.services.channel_service import ChannelService
from app.repositories.channel_repository import ChannelRepository
from app.models.channel import Channel
from datetime import datetime
from fastapi import status
from app.api.errors.channel import ChannelAlreadyExistsError, InvalidChannelNameError


client = TestClient(app)


def assert_error_format(body, expected_status: int = status.HTTP_400_BAD_REQUEST):
    """
    Asserts that the error response follows the RFC 7807 Problem
    Details format.
    """

    assert body["type"] == "about:blank"
    assert "title" in body
    assert body["status"] == expected_status
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
        ChannelRepository,
        "find_by_name_ci",
        return_value=Channel(
            id=1, name="Test Channel", createdAt=datetime(2026, 8, 23, 18, 0, 0)
        ),
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


def test_create_channel_with_only_spaces():
    channel_name = "   "

    response = client.post("/channels", json={"name": channel_name})

    assert_error_format(response.json())


def test_channel_name_with_null_character():
    channel_name = "Channel\x00Name"

    response = client.post("/channels", json={"name": channel_name})

    assert_error_format(response.json(), status.HTTP_422_UNPROCESSABLE_CONTENT)
