from app.repositories.message_repository import MessageRepository
from app.repositories.channel_repository import ChannelRepository
from app.models.message import Message
from app.api.errors.channel import ChannelNotFoundError
from app.api.errors.message import (
    InvalidMessageContentError,
    MessageNotFoundError,
    UnauthorizedMessageEditError,
    MessageNotInChannelError,
)
from loguru import logger


class MessageService:
    @staticmethod
    def create_message(channel_id: int, author_id: int, content: str):
        """Creates a new message in the specified channel."""

        if not content.strip() or len(content) > 2000:
            raise InvalidMessageContentError()

        logger.info(f'Creating message in channel with ID: "{channel_id}".')

        message = MessageRepository.create(channel_id, author_id, content)

        logger.info(f'Message created successfully in channel with ID: "{channel_id}".')

        return message

    @staticmethod
    def edit_message(
        channel_id: int, message_id: int, author_id: int, new_content: str
    ):
        """Edits an existing message with the given ID."""

        if not new_content.strip() or len(new_content) > 2000:
            raise InvalidMessageContentError()

        logger.info(f'Editing message with ID: "{message_id}".')

        message = MessageRepository.find_by_id(message_id)

        if not message:
            raise MessageNotFoundError(message_id)
        if message.channelId != channel_id:
            raise MessageNotInChannelError(message_id, channel_id)
        if message.authorId != author_id:
            raise UnauthorizedMessageEditError(message_id, author_id)

        logger.info(f'Updating message with ID: "{message_id}".')

        message = MessageRepository.update(message_id, new_content)

        logger.info(f'Message with ID: "{message_id}" updated successfully.')

        return message

    @staticmethod
    def get_messages_by_channel(channel_id: int) -> list[Message]:
        """Retrieves all messages for a specific channel."""

        if not ChannelRepository.exists_by_id(channel_id):
            raise ChannelNotFoundError(channel_id)

        logger.info(f'Retrieving messages for channel with ID: "{channel_id}".')

        messages = MessageRepository.find_by_channel_id(channel_id)

        logger.info(
            f'Retrieved {len(messages)} messages for channel with ID: "{channel_id}".'
        )

        return messages
