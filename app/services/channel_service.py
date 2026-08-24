from loguru import logger
from app.repositories.channel_repository import ChannelRepository
from app.api.errors.channel import ChannelAlreadyExistsError
from app.models.channel import Channel


class ChannelService:
    @staticmethod
    def create_channel(channel_name: str) -> Channel:
        """Creates a new channel with the given name."""

        logger.info(f'Creating channel with name: "{channel_name}"')

        existing_channel = ChannelRepository.find_by_name_ci(channel_name)

        if existing_channel:
            logger.error(f'Channel with name: "{channel_name}" already exists')
            raise ChannelAlreadyExistsError(channel_name)

        channel = ChannelRepository.create(channel_name)

        logger.info(f'Channel of name: "{channel_name}" created successfully.')

        return channel
