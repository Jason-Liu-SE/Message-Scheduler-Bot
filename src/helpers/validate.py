import os


def validate_channel(channel: str) -> None:
    if not channel.isdigit():  # ensure that the provided value could be a channel
        raise ValueError("The channel must be a numerical value")


def is_development() -> None:
    is_dev = os.getenv("IS_DEV")

    return is_dev != None and is_dev.lower() == "true"
