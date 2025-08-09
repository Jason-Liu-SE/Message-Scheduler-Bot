from functools import cmp_to_key
import functools
from typing import Any, Awaitable, Callable, Coroutine
import discord
from discord import app_commands

from commands.command_bot import CommandBot
from helpers.message_scheduler.mongo_utils import *
from helpers.message_utils import *
from helpers.validate import has_role


# Expected minimum signature of 'func'
# (self, interaction: discord.Interaction, ...)
def enrich_command(
    func: Callable[..., Coroutine[Any, Any, Any]],
) -> Callable[..., Coroutine[Any, Any, Any]]:
    # Since the intended behaviour for this decorator is for app_commands to supply arguments
    # to wrapper, the only *args will be a 'self' object and 'discord.Interaction' object. All
    # other arguments are **kwargs.
    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> None:
        try:
            self_obj: CommandBot = args[0] if args else None
            interaction = args[1] if args else None

            @catch_and_log(interaction=interaction)
            async def inner() -> None:
                await handle_command(
                    func,
                    interaction,
                    self_obj._allowed_roles,
                    # Arguments for func
                    self_obj,
                    interaction,
                    **kwargs,
                )

            await inner()
        except Exception as e:
            Logger.error(e)

    return wrapper


async def handle_command(
    cmd: Callable[..., Awaitable[Any]],
    interaction: discord.Interaction,
    allowed_roles: list,
    *cmd_args,
    **kwargs,
) -> None:
    await interaction.response.defer()

    if not has_role(interaction, allowed_roles):
        await send_error(interaction, f"{interaction.user.mention}: insufficient role")
        return

    @catch_and_log(interaction=interaction)
    async def run_cmd() -> None:
        await cmd(*cmd_args, **kwargs)

    await run_cmd()


def catch_and_log(interaction: discord.Interaction | None):
    def wrapper(func):
        async def inner(*args, **kwargs) -> None:
            try:
                await func(*args, **kwargs)
            except (
                ValueError
            ) as e:  # this only throws if the user provided invalid input
                if interaction:
                    await send_error(interaction, e)
                else:
                    Logger.error(
                        f"catch_and_log wasn't provided an interaction and ValueError-failed with: {e}"
                    )
            except Exception as e:
                Logger.exception(e)

                if interaction:
                    await send_error(interaction, "An error occurred.")

        return inner

    return wrapper


def generate_autocomplete(
    items: list,
    callback: Callable[
        [discord.Interaction, str], Awaitable[list[app_commands.Choice]]
    ] = None,
    const_items: dict = {},
) -> Callable[[discord.Interaction, str], list]:
    async def autocomplete(interaction: discord.Interaction, current: str) -> list:
        choices = []

        for name, value in const_items.items():
            choices.append(app_commands.Choice(name=f"{name}", value=value))

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
