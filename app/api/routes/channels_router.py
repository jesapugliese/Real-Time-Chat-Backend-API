from fastapi import APIRouter, status, HTTPException

from app.schemas.channel import ChannelCreateRequest, ChannelResponse
from app.services.channel_service import ChannelService
from app.api.errors.channel import InvalidChannelNameError


router = APIRouter(prefix="/channels")


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Create a new channel",
)
def create_channel(request: ChannelCreateRequest) -> dict:
    """Create a new channel with the given name."""

    channel_name = request.name

    if not channel_name or len(channel_name) < 1 or len(channel_name) > 50:
        raise InvalidChannelNameError(channel_name)

    channel = ChannelService.create_channel(channel_name)

    return {
        "data": ChannelResponse(
            id=channel.id, name=channel.name, createdAt=channel.createdAt
        )
    }
