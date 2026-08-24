from app.api.errors.app_error import AppError
from fastapi import Request, status, WebSocket
from fastapi.responses import JSONResponse

from app.api.errors.channel import (
    InvalidChannelNameError,
    ChannelAlreadyExistsError,
)

from app.api.errors.message import (
    InvalidMessageContentError,
    MessageNotFoundError,
    MessageNotInChannelError,
    UnauthorizedMessageEditError,
)


class ErrorHandler:
    """
    Class that provides centralized exception handling for the API.

    Converts application exceptions into HTTP responses following the
    RFC 7807 Problem Details format.
    """

    @staticmethod
    def error_response(
        request: Request,
        status_code: int,
        title: str,
        detail: str,
    ) -> JSONResponse:
        """Creates an RFC 7807 Problem Details response."""

        return JSONResponse(
            status_code=status_code,
            media_type="application/problem+json",
            content={
                "type": "about:blank",
                "title": title,
                "status": status_code,
                "detail": detail,
                "instance": request.url.path,
            },
        )

    @staticmethod
    async def websocket_error_response(
        websocket: WebSocket,
        exc: AppError,
        channel_id: int,
    ) -> None:
        """Sends an RFC 7807 Problem Details response over a WebSocket."""

        await websocket.send_json(
            {
                "type": "about:blank",
                "title": exc.title,
                "status": exc.status_code,
                "detail": exc.detail,
                "instance": f"/channels/{channel_id}/ws",
            }
        )

    @staticmethod
    def register_error_handlers(app) -> None:
        """Registers exception handlers for the FastAPI application."""

        app.add_exception_handler(
            InvalidChannelNameError,
            ErrorHandler.handle_invalid_channel_name_error,
        )
        app.add_exception_handler(
            ChannelAlreadyExistsError,
            ErrorHandler.handle_channel_already_exists_error,
        )

    @staticmethod
    async def handle_invalid_channel_name_error(
        request: Request, exc: InvalidChannelNameError
    ) -> JSONResponse:
        return ErrorHandler.error_response(
            request=request,
            status_code=status.HTTP_400_BAD_REQUEST,
            title="Invalid Channel Name",
            detail=f"Channel name '{exc.channel_name}' is invalid.",
        )

    @staticmethod
    async def handle_channel_already_exists_error(
        request: Request, exc: ChannelAlreadyExistsError
    ) -> JSONResponse:
        return ErrorHandler.error_response(
            request=request,
            status_code=status.HTTP_400_BAD_REQUEST,
            title="Channel Already Exists",
            detail=f"Channel with name {exc.channel_name} already exists.",
        )
