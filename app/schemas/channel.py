from datetime import datetime
from pydantic import BaseModel, field_serializer, field_validator


class ChannelCreateRequest(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        if "\x00" in value:
            raise ValueError("Name must not contain null characters.")
        return value


class ChannelResponse(BaseModel):
    id: int
    name: str
    createdAt: datetime

    @field_serializer("createdAt")
    def serialize_created_at(self, value: datetime) -> str:
        """
        Serializes the createdAt field to an ISO 8601 string with
        milliseconds precision and 'Z' suffix for UTC timezone.
        """

        return value.isoformat(timespec="milliseconds").replace("+00:00", "Z")


class ChannelCreateResponse(BaseModel):
    data: ChannelResponse


class ChannelListResponse(BaseModel):
    data: list[ChannelResponse]
