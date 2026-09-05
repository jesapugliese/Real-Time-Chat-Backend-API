import pytest
from datetime import datetime
from unittest.mock import patch

from fastapi.testclient import TestClient
from fastapi import WebSocketDisconnect, status

from app.main import app
from app.models.message import Message
from app.services.message_service import MessageService
from app.services.channel_service import ChannelService
from app.api.errors.message import InvalidMessageContentError


client = TestClient(app)


def test_connect_to_channel_websocket():
    with (
        patch.object(ChannelService, "exists_by_id", return_value=True),
        patch.object(MessageService, "get_messages_by_channel", return_value=[]),
    ):
        with client.websocket_connect(f"/channels/1/ws") as websocket:
            assert websocket is not None


def test_send_message():
    with (
        patch.object(ChannelService, "exists_by_id", return_value=True),
        patch.object(
            MessageService,
            "create_message",
            return_value=Message(
                id=1,
                channelId=1,
                authorId=1,
                content="This a message",
                createdAt=datetime(2026, 8, 23, 18, 0, 0),
                editedAt=None,
            ),
        ) as mock_create_message,
        patch.object(MessageService, "get_messages_by_channel", return_value=[]),
    ):
        with client.websocket_connect(f"/channels/1/ws") as websocket:
            websocket.send_json(
                {
                    "id": None,
                    "channelId": 1,
                    "authorId": 1,
                    "content": "This a message",
                }
            )

            response = websocket.receive_json()

    assert response["id"] == 1
    assert response["channelId"] == 1
    assert response["authorId"] == 1
    assert response["content"] == "This a message"
    assert response["editedAt"] is None

    mock_create_message.assert_called_once_with(
        channel_id=1, author_id=1, content="This a message"
    )


def test_send_empty_message():
    with (
        patch.object(ChannelService, "exists_by_id", return_value=True),
        patch.object(
            MessageService,
            "create_message",
            side_effect=InvalidMessageContentError(),
        ),
        patch.object(MessageService, "get_messages_by_channel", return_value=[]),
    ):
        with client.websocket_connect(f"/channels/1/ws") as websocket:
            websocket.send_json(
                {
                    "id": None,
                    "channelId": 1,
                    "authorId": 1,
                    "content": "",
                }
            )

            response = websocket.receive_json()

    assert "error" in response


def test_edit_message():
    with (
        patch.object(ChannelService, "exists_by_id", return_value=True),
        patch.object(
            MessageService,
            "edit_message",
            return_value=Message(
                id=1,
                channelId=1,
                authorId=1,
                content="Edited message",
                createdAt=datetime(2026, 8, 23, 18, 0, 0),
                editedAt=datetime(2026, 8, 23, 18, 5, 0),
            ),
        ) as mock_edit_message,
        patch.object(MessageService, "get_messages_by_channel", return_value=[]),
    ):
        with client.websocket_connect(f"/channels/1/ws") as websocket:
            websocket.send_json(
                {
                    "id": 1,
                    "channelId": 1,
                    "authorId": 1,
                    "content": "Edited message",
                }
            )

            response = websocket.receive_json()

    assert response["id"] == 1
    assert response["channelId"] == 1
    assert response["authorId"] == 1
    assert response["content"] == "Edited message"
    assert response["editedAt"] is not None

    mock_edit_message.assert_called_once_with(
        channel_id=1, message_id=1, author_id=1, new_content="Edited message"
    )


def test_message_is_broadcasted_to_all_connected_clients():
    with (
        patch.object(ChannelService, "exists_by_id", return_value=True),
        patch.object(
            MessageService,
            "create_message",
            return_value=Message(
                id=1,
                channelId=1,
                authorId=1,
                content="This a message",
                createdAt=datetime(2026, 8, 23, 18, 0, 0),
                editedAt=None,
            ),
        ),
        patch.object(MessageService, "get_messages_by_channel", return_value=[]),
    ):
        with client.websocket_connect(f"/channels/1/ws") as websocket1:
            with client.websocket_connect(f"/channels/1/ws") as websocket2:
                websocket1.send_json(
                    {
                        "id": None,
                        "channelId": 1,
                        "authorId": 1,
                        "content": "This a message",
                    }
                )

                response1 = websocket1.receive_json()
                response2 = websocket2.receive_json()

    assert response1["id"] == 1
    assert response2["id"] == 1
    assert response1["content"] == "This a message"
    assert response2["content"] == "This a message"


def test_channel_not_found():
    with (
        patch.object(ChannelService, "exists_by_id", return_value=False),
        patch.object(MessageService, "get_messages_by_channel", return_value=[]),
    ):
        with pytest.raises(WebSocketDisconnect) as exc:
            with client.websocket_connect(f"/channels/999/ws"):
                pass

    assert exc.value.code == 1008


def test_get_messages_by_channel():
    with (
        patch.object(ChannelService, "exists_by_id", return_value=True),
        patch.object(
            MessageService,
            "get_messages_by_channel",
            return_value=[
                Message(
                    id=1,
                    channelId=1,
                    authorId=1,
                    content="Message 1",
                    createdAt=datetime(2026, 8, 23, 18, 0, 0),
                    editedAt=None,
                ),
                Message(
                    id=2,
                    channelId=1,
                    authorId=2,
                    content="Message 2",
                    createdAt=datetime(2026, 8, 23, 18, 5, 0),
                    editedAt=None,
                ),
            ],
        ),
    ):
        with client.websocket_connect(f"/channels/1/ws"):
            response = client.get("/channels/1/messages")

    body = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(body["data"]) == 2
    assert body["data"][0]["content"] == "Message 1"
    assert body["data"][1]["content"] == "Message 2"


def test_websocket_invalid_json():
    with (
        patch.object(ChannelService, "exists_by_id", return_value=True),
        patch.object(MessageService, "get_messages_by_channel", return_value=[]),
    ):
        with client.websocket_connect("/channels/1/ws") as websocket:
            websocket.send_text('{"authorId": 1, "content": "Hola"')

            response = websocket.receive_json()

            assert "error" in response


def test_websocket_message_with_null_character():
    with (
        patch.object(ChannelService, "exists_by_id", return_value=True),
        patch.object(MessageService, "get_messages_by_channel", return_value=[]),
    ):
        with client.websocket_connect("/channels/1/ws") as websocket:
            websocket.send_json(
                {
                    "authorId": 1,
                    "content": "Hola\x00mundo",
                }
            )

            response = websocket.receive_json()

            assert "error" in response


def test_send_message_with_only_spaces():
    with (
        patch.object(ChannelService, "exists_by_id", return_value=True),
        patch.object(MessageService, "get_messages_by_channel", return_value=[]),
    ):
        with client.websocket_connect(f"/channels/1/ws") as websocket:
            websocket.send_json(
                {
                    "id": None,
                    "channelId": 1,
                    "authorId": 1,
                    "content": "     ",
                }
            )

            response = websocket.receive_json()

    assert "error" in response


def test_send_message_exceeding_max_length():
    long_content = "a" * 2001

    with (
        patch.object(ChannelService, "exists_by_id", return_value=True),
        patch.object(MessageService, "get_messages_by_channel", return_value=[]),
    ):
        with client.websocket_connect(f"/channels/1/ws") as websocket:
            websocket.send_json(
                {
                    "id": None,
                    "channelId": 1,
                    "authorId": 1,
                    "content": long_content,
                }
            )

            response = websocket.receive_json()

    assert "error" in response
