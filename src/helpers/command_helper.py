from typing import Any, Awaitable, Callable
import discord

from helpers.message_scheduler.mongo_utils import *
from helpers.message_utils import *
from helpers.validate import has_role


async def handle_command(
    cmd: Callable[..., Awaitable[Any]],
    interaction: discord.Interaction,
    allowed_roles: list,
    *cmd_args
) -> None:
    if not has_role(interaction, allowed_roles):
        await send_embedded_message(
            interaction, 0xFF0000, {"title": "ERROR", "desc": "Insufficient role"}
        )
        return

    try:
        # creating a schedule and message object for new servers
        await register_server_with_db(interaction)

        # handling command
        await cmd(interaction, *cmd_args)
    except ValueError as e:  # this only throws if the user provided invalid arguments
        Logger.exception(e)
        await send_embedded_message(
            interaction, 0xFF0000, {"title": "ERROR", "desc": e}
        )
    except TypeError as e:
        Logger.exception(e)
        await send_embedded_message(
            interaction, 0xFF0000, {"title": "ERROR", "desc": e}
        )
    except RuntimeError as e:
        Logger.exception(e)
        await send_embedded_message(
            interaction, 0xFF0000, {"title": "ERROR", "desc": e}
        )
    except Exception as e:
        Logger.exception(e)
        await send_embedded_message(
            interaction,
            0xFF0000,
            {
                "title": "ERROR",
                "desc": "An error occurred. Command will be ignored.",
            },
        )
