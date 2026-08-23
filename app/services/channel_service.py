from app.repositories.channel_repository import ChannelRepository
from app.api.errors.channel import ChannelAlreadyExistsError
from app.models.channel import Channel


class ChannelService:
    @staticmethod
    def create_channel(channel_name: str) -> Channel:
        """Creates a new channel with the given name."""

        existing_channel = ChannelRepository.find_by_name_ci(channel_name)

        if existing_channel:
            raise ChannelAlreadyExistsError(channel_name)

        return ChannelRepository.create(channel_name)
