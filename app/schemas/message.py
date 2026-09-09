from datetime import datetime
from pydantic import BaseModel, Field, field_validator


INT32_MIN = -2_147_483_648
INT32_MAX = 2_147_483_647


class SendOrEditMessageEvent(BaseModel):
    id: int | None = Field(default=None, ge=INT32_MIN, le=INT32_MAX)
    authorId: int = Field(..., ge=INT32_MIN, le=INT32_MAX)
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
