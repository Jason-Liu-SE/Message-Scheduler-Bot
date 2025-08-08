import discord

from helpers.logger import Logger
from helpers.message_utils import send_error


async def handle_error(
    interaction: discord.Interaction, error_msg: str, error: any
) -> None:
    Logger.error(f"{error_msg}: {error}")
    await send_error(interaction, error_msg)
