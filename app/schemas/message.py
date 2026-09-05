from datetime import datetime
from pydantic import BaseModel, field_validator


class SendOrEditMessageEvent(BaseModel):
    id: int | None = None
    authorId: int
    content: str

    @field_validator("content")
    @classmethod
    def validate_content(cls, value: str) -> str:
        if "\x00" in value:
            raise ValueError("Content must not contain null characters.")
        return value


class MessageResponse(BaseModel):
    id: int
    channelId: int
    authorId: int
    content: str
    createdAt: datetime
    editedAt: datetime | None = None


class MessageListResponse(BaseModel):
    data: list[MessageResponse]
