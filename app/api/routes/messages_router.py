from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from loguru import logger
from app.schemas.message import (
    SendOrEditMessageEvent,
    MessageResponse,
)
from app.services.message_service import MessageService
from app.services.channel_service import ChannelService
from app.api.websocket_manager import websocket_manager
from app.api.errors.app_error import AppError
from app.api.error_handler import ErrorHandler


router = APIRouter(prefix="/channels")


@router.websocket("/{channelId}/ws")
async def channel_websocket(websocket: WebSocket, channelId: int):
    """WebSocket endpoint for a specific channel."""

    logger.info(f"WebSocket connection request received for channel ID: {channelId}")

    if not ChannelService.exists_by_id(channelId):
        logger.warning(f"Channel with ID: {channelId} does not exist.")
        await websocket.close(code=1008)
        return

    await websocket_manager.connect(channelId, websocket)

    try:
        while True:
            try:
                data = await websocket.receive_json()

                logger.info(
                    f"Received data from WebSocket for channel ID: {channelId}: {data}"
                )

                event = SendOrEditMessageEvent(**data)

                if event.id is None:
                    message = MessageService.create_message(
                        channel_id=channelId,
                        author_id=event.authorId,
                        content=event.content,
                    )
                else:
                    message = MessageService.edit_message(
                        channel_id=channelId,
                        message_id=event.id,
                        author_id=event.authorId,
                        new_content=event.content,
                    )

                response = MessageResponse(
                    id=message.id,
                    channelId=message.channelId,
                    authorId=message.authorId,
                    content=message.content,
                    createdAt=message.createdAt,
                    editedAt=message.editedAt,
                )

                await websocket_manager.broadcast(
                    channelId, response.model_dump(mode="json")
                )
            except AppError as exc:
                logger.warning(
                    f"AppError occurred for channel ID: {channelId}: {exc.detail}"
                )
                await ErrorHandler.websocket_error_response(websocket, exc)
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for channel ID: {channelId}")
        websocket_manager.disconnect(channelId, websocket)


@router.get(
    "/{channelId}/messages",
    status_code=status.HTTP_200_OK,
    summary="Retrieve the message history of a channel",
)
def get_channel_messages(channelId: int) -> list[MessageResponse]:
    """Retrieve the message history of a specific channel."""

    logger.info(f"Received request to retrieve messages for channel ID: {channelId}")

    messages = MessageService.get_messages_by_channel(channelId)

    return [
        MessageResponse(
            id=message.id,
            channelId=message.channelId,
            authorId=message.authorId,
            content=message.content,
            createdAt=message.createdAt,
            editedAt=message.editedAt,
        )
        for message in messages
    ]
