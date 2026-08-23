from datetime import datetime


class Channel:
    def __init__(self, id: int, name: str, createdAt: datetime):
        self.id = id
        self.name = name
        self.createdAt = createdAt
