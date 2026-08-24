from app.main import app
from app.repositories.message_repository import MessageRepository
from fastapi import status
from fastapi.testclient import TestClient


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
