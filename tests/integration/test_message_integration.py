from app.main import app
from app.repositories.message_repository import MessageRepository
from fastapi import status
from fastapi.testclient import TestClient


def assert_error_format(body, status_code):
    """
    Asserts that the error response follows the RFC 7807 Problem
    Details format.
    """

    assert body["type"] == "about:blank"
    assert "title" in body
    assert body["status"] == status_code
    assert "detail" in body
    assert "instance" in body


def test_send_message_integration():
    with TestClient(app) as client:
        channel_response = client.post(
            "/channels",
            json={"name": "message-integration-channel"},
        )

        assert channel_response.status_code == status.HTTP_201_CREATED

        channel_id = channel_response.json()["data"]["id"]

        with client.websocket_connect(f"/channels/{channel_id}/ws") as websocket:
            websocket.send_json(
                {
                    "authorId": 1,
                    "content": "Message Integration Test",
                }
            )

            response = websocket.receive_json()

    assert response["id"] is not None
    assert response["authorId"] == 1
    assert response["content"] == "Message Integration Test"
    assert response["createdAt"] is not None
    assert response["editedAt"] is None

    persisted_message = MessageRepository.find_by_id(response["id"])

    assert persisted_message is not None
    assert persisted_message.id == response["id"]
    assert persisted_message.channelId == channel_id
    assert persisted_message.authorId == 1
    assert persisted_message.content == "Message Integration Test"
    assert persisted_message.editedAt is None


def test_edit_message_integration():
    with TestClient(app) as client:
        channel_response = client.post(
            "/channels",
            json={"name": "edit-message-integration-channel"},
        )

        channel_id = channel_response.json()["data"]["id"]

        with client.websocket_connect(f"/channels/{channel_id}/ws") as websocket:
            websocket.send_json(
                {
                    "authorId": 1,
                    "content": "Original Message",
                }
            )

            create_response = websocket.receive_json()

            message_id = create_response["id"]

            websocket.send_json(
                {
                    "id": message_id,
                    "authorId": 1,
                    "content": "Edited Message",
                }
            )

            edit_response = websocket.receive_json()

    assert edit_response["id"] == message_id
    assert edit_response["authorId"] == 1
    assert edit_response["content"] == "Edited Message"
    assert edit_response["createdAt"] is not None
    assert edit_response["editedAt"] is not None

    persisted_message = MessageRepository.find_by_id(message_id)

    assert persisted_message is not None
    assert persisted_message.id == message_id
    assert persisted_message.channelId == channel_id
    assert persisted_message.authorId == 1
    assert persisted_message.content == "Edited Message"
    assert persisted_message.editedAt is not None


def test_get_messages_by_channel_integration():
    with TestClient(app) as client:
        channel_response = client.post(
            "/channels",
            json={"name": "get-messages-integration-channel"},
        )

        channel_id = channel_response.json()["data"]["id"]

        with client.websocket_connect(f"/channels/{channel_id}/ws") as websocket:
            websocket.send_json(
                {
                    "authorId": 1,
                    "content": "First Message",
                }
            )
            websocket.receive_json()

            websocket.send_json(
                {
                    "authorId": 2,
                    "content": "Second Message",
                }
            )
            websocket.receive_json()

        get_messages_response = client.get(f"/channels/{channel_id}/messages")

    assert get_messages_response.status_code == status.HTTP_200_OK

    messages = get_messages_response.json()

    assert len(messages["data"]) == 2
    assert messages["data"][0]["content"] == "First Message"
    assert messages["data"][1]["content"] == "Second Message"


def test_not_get_messages_by_other_channels_integration():
    with TestClient(app) as client:
        channel_response1 = client.post(
            "/channels",
            json={"name": "channel-1"},
        )
        channel_id1 = channel_response1.json()["data"]["id"]

        channel_response2 = client.post(
            "/channels",
            json={"name": "channel-2"},
        )
        channel_id2 = channel_response2.json()["data"]["id"]

        with client.websocket_connect(f"/channels/{channel_id1}/ws") as websocket1:
            websocket1.send_json(
                {
                    "authorId": 1,
                    "content": "Message in Channel 1",
                }
            )
            websocket1.receive_json()

        with client.websocket_connect(f"/channels/{channel_id2}/ws") as websocket2:
            websocket2.send_json(
                {
                    "authorId": 2,
                    "content": "Message in Channel 2",
                }
            )
            websocket2.receive_json()

        get_messages_response1 = client.get(f"/channels/{channel_id1}/messages")
        get_messages_response2 = client.get(f"/channels/{channel_id2}/messages")

    assert get_messages_response1.status_code == status.HTTP_200_OK
    assert get_messages_response2.status_code == status.HTTP_200_OK

    messages_channel_1 = get_messages_response1.json()
    messages_channel_2 = get_messages_response2.json()

    assert len(messages_channel_1["data"]) == 1
    assert messages_channel_1["data"][0]["content"] == "Message in Channel 1"

    assert len(messages_channel_2["data"]) == 1
    assert messages_channel_2["data"][0]["content"] == "Message in Channel 2"


def test_get_messages_by_channel_not_found():
    with TestClient(app) as client:
        with client.websocket_connect(f"/channels/1/ws"):
            response = client.get("/channels/999/messages")

    assert_error_format(response.json(), status.HTTP_404_NOT_FOUND)
