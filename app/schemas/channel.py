from datetime import datetime
from pydantic import BaseModel, field_serializer


class ChannelCreateRequest(BaseModel):
    name: str


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
