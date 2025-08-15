import os
import inspect
import discord


def validate_channel(channel: str) -> None:
    if not channel.isdigit():  # ensure that the provided value could be a channel
        raise ValueError("The channel must be a numerical value")


def is_development() -> bool:
    is_dev = os.getenv("IS_DEV")

    return is_dev != None and is_dev.lower() == "true"


# returns whether interaction user has a role in allowed_roles or not
def has_role(interaction: discord.Interaction, allowed_roles: list) -> bool:
    allowed_roles_lower = []

    for role in allowed_roles:
        allowed_roles_lower.append(role if not type(role) is str else role.lower())

    return any(
        (role.id in allowed_roles_lower or role.name.lower() in allowed_roles_lower)
        for role in interaction.user.roles
    )


def filter_valid_kwargs(func, **kwargs):
    sig = inspect.signature(func)
    valid_params = sig.parameters
    filtered_kwargs = {k: v for k, v in kwargs.items() if k in valid_params}
    return func(**filtered_kwargs)
