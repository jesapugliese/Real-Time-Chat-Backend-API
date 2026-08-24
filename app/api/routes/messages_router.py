from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from loguru import logger
from app.schemas.message import (
    SendOrEditMessageEvent,
    MessageResponse,
)
from app.services.message_service import MessageService
from app.api.websocket_manager import websocket_manager
from app.api.errors.app_error import AppError
from app.api.error_handler import ErrorHandler


router = APIRouter(prefix="/channels")


@router.websocket("/{channel_id}/ws")
async def channel_websocket(websocket: WebSocket, channel_id: int):
    """WebSocket endpoint for a specific channel."""

    logger.info(f"WebSocket connection request received for channel ID: {channel_id}")

    await websocket_manager.connect(channel_id, websocket)

    try:
        while True:
            data = await websocket.receive_json()

            logger.info(
                f"Received data from WebSocket for channel ID: {channel_id}: {data}"
            )

            event = SendOrEditMessageEvent(**data)

            if event.id is None:
                message = MessageService.create_message(
                    channel_id=channel_id,
                    author_id=event.authorId,
                    content=event.content,
                )
            else:
                message = MessageService.edit_message(
                    channel_id=channel_id,
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
                channel_id, response.model_dump(mode="json")
            )
    except AppError as exc:
        logger.error(
            f"AppError occurred for channel ID: {channel_id}: {exc.title} - {exc.detail}"
        )
        await ErrorHandler.websocket_error_response(websocket, exc, channel_id)
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for channel ID: {channel_id}")
        websocket_manager.disconnect(channel_id, websocket)
