from datetime import datetime


class Message:
    def __init__(
        self,
        id: int,
        channelId: int,
        authorId: int,
        content: str,
        createdAt: datetime,
        editedAt: datetime | None = None,
    ):
        self.id = id
        self.channelId = channelId
        self.authorId = authorId
        self.content = content
        self.createdAt = createdAt
        self.editedAt = editedAt
