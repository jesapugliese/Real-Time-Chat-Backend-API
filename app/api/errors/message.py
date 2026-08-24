from fastapi import status
from app.api.errors.app_error import AppError


class InvalidMessageContentError(AppError):
    def __init__(self):
        self.detail = (
            "Message content cannot be empty or exceed the maximum allowed length."
        )
        super().__init__(self.detail)


class MessageNotFoundError(AppError):
    def __init__(self, message_id: int):
        self.message_id = message_id
        self.detail = f"Message with ID {message_id} not found."
        super().__init__(self.detail)


class UnauthorizedMessageEditError(AppError):
    def __init__(self, message_id: int, user_id: int):
        self.message_id = message_id
        self.user_id = user_id
        self.detail = f"User with ID {user_id} is not authorized to edit message with ID {message_id}."
        super().__init__(self.detail)


class MessageNotInChannelError(AppError):
    def __init__(self, message_id: int, channel_id: int):
        self.message_id = message_id
        self.channel_id = channel_id
        self.detail = f"Message with ID {message_id} does not belong to channel with ID {channel_id}."
        super().__init__(self.detail)
