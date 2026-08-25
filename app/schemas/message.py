from datetime import datetime
from pydantic import BaseModel


class SendOrEditMessageEvent(BaseModel):
    id: int | None = None
    authorId: int
    content: str


class MessageResponse(BaseModel):
    id: int
    channelId: int
    authorId: int
    content: str
    createdAt: datetime
    editedAt: datetime | None = None

class MessageListResponse(BaseModel):
    data: list[MessageResponse]
