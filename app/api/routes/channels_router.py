from fastapi import APIRouter, status
from loguru import logger
from app.schemas.channel import *
from app.services.channel_service import ChannelService
from app.api.errors.channel import InvalidChannelNameError


router = APIRouter(prefix="/channels")


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Create a new channel",
)
def create_channel(request: ChannelCreateRequest) -> ChannelCreateResponse:
    """Create a new channel with the given name."""

    logger.info(f'Received request to create channel with name: "{request.name}"')

    channel_name = request.name

    if not channel_name or len(channel_name) < 1 or len(channel_name) > 50:
        logger.error(f'Invalid channel name: "{channel_name}"')
        raise InvalidChannelNameError(channel_name)

    channel = ChannelService.create_channel(channel_name)

    return ChannelCreateResponse(
        data=ChannelResponse(
            id=channel.id, name=channel.name, createdAt=channel.createdAt
        )
    )


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    summary="Retrieve all channels",
)
def get_all_channels() -> ChannelListResponse:
    """Retrieve all channels."""

    logger.info("Received request to retrieve all channels")

    channels = ChannelService.get_all_channels()

    return ChannelListResponse(
        data=[
            ChannelResponse(
                id=channel.id, name=channel.name, createdAt=channel.createdAt
            )
            for channel in channels
        ]
    )
