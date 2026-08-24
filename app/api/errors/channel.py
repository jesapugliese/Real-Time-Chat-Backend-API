class InvalidChannelNameError(Exception):
    def __init__(self, channel_name: str):
        self.channel_name = channel_name


class ChannelAlreadyExistsError(Exception):
    def __init__(self, channel_name: str):
        self.channel_name = channel_name


class ChannelNotFoundError(Exception):
    def __init__(self, channel_id: int):
        self.channel_id = channel_id
