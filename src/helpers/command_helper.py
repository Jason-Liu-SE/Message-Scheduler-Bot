from functools import cmp_to_key
from typing import Any, Awaitable, Callable
import discord
from discord import app_commands

from helpers.colours import Colour
from helpers.message_scheduler.mongo_utils import *
from helpers.message_utils import *
from helpers.ticket_bot.mongo_utils import register_user_with_db
from helpers.validate import has_role


async def handle_command(
    cmd: Callable[..., Awaitable[Any]],
    interaction: discord.Interaction,
    allowed_roles: list,
    *cmd_args,
) -> None:
    await interaction.response.defer()

    if not has_role(interaction, allowed_roles):
        await send_error(interaction, "Insufficient role")
        return

    try:
        # handling command
        await cmd(interaction, *cmd_args)
    except ValueError as e:  # this only throws if the user provided invalid input
        Logger.error(e)
        await send_error(interaction, e)
    except Exception as e:
        Logger.exception(e)
        await send_error(interaction, "An error occurred.")


def generate_autocomplete(
    items: list,
    callback: Callable[
        [discord.Interaction, str], Awaitable[list[app_commands.Choice]]
    ] = None,
) -> Callable[[discord.Interaction, str], list]:
    async def autocomplete(interaction: discord.Interaction, current: str) -> list:
        choices = []

        for item in items:
            if current.lower() in f"{item}":
                choices.append(app_commands.Choice(name=f"{item}", value=item))

        choices = choices[:25]

        if callback and len(choices) < 25:
            choices.extend((await callback(interaction, current))[: 25 - len(choices)])

        return choices

    return autocomplete


def sort_schedules_by_date(schedule: dict, is_ascending: bool = True) -> dict:
    invert = 1 if is_ascending else -1

    return dict(
        sorted(
            schedule.items(),
            key=cmp_to_key(
                lambda a, b: 1 * invert if a[1]["time"] > b[1]["time"] else -1 * invert
            ),
        )
    )
