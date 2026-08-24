from loguru import logger
from app.repositories.channel_repository import ChannelRepository
from app.api.errors.channel import InvalidChannelNameError, ChannelAlreadyExistsError
from app.models.channel import Channel


class ChannelService:
    @staticmethod
    def create_channel(channel_name: str) -> Channel:
        """Creates a new channel with the given name."""

        if not channel_name or len(channel_name) < 1 or len(channel_name) > 50:
            raise InvalidChannelNameError(channel_name)

        logger.info(f'Creating channel with name: "{channel_name}"')

        existing_channel = ChannelRepository.find_by_name_ci(channel_name)

        if existing_channel:
            raise ChannelAlreadyExistsError(channel_name)

        channel = ChannelRepository.create(channel_name)

        logger.info(f'Channel of name: "{channel_name}" created successfully.')

        return channel

    @staticmethod
    def get_all_channels() -> list[Channel]:
        """Retrieves all channels from the database."""

        logger.info("Retrieving all channels from the database")

        channels = ChannelRepository.get_all()

        logger.info(f"Retrieved {len(channels)} channels from the database")

        return channels

    @staticmethod
    def exists_by_id(channel_id: int) -> bool:
        """Checks if a channel with the given ID exists."""

        logger.info(f'Checking if channel with ID: "{channel_id}" exists')

        exists = ChannelRepository.exists_by_id(channel_id)

        logger.info(f'Channel with ID: "{channel_id}" exists: {exists}')

        return exists
