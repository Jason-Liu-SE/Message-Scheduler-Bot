async def validate_channel(channel: str) -> None:
    if not channel.isdigit():  # ensure that the provided value could be a channel
        raise ValueError("The channel must be a numerical value")
