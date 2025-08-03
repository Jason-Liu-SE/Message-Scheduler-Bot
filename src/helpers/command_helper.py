import discord
from discord.ext import commands
from discord import app_commands

from helpers.message_scheduler.mongo_utils import *
from helpers.message_utils import *


async def handle_command(
    cmd, interaction: discord.Interaction, allowed_roles, **cmd_args
):
    # role check
    if not any(role.id in allowed_roles for role in interaction.user.roles):
        await interaction.response.send_message(
            "Error: insufficient role", ephemeral=True
        )
        return

    # creating a schedule and message object for new servers
    await register_server_with_db(interaction)
    await interaction.response.send_message("Add")
    # interpreting commands
    try:
        cmd(interaction, cmd_args)
    except ValueError as e:  # this only throws if the user provided invalid arguments
        Logger.error(e)
        await send_embedded_message(ctx, 0xFF0000, {"title": "ERROR", "desc": e})
    except TypeError as e:
        Logger.error(e)
        await send_embedded_message(ctx, 0xFF0000, {"title": "ERROR", "desc": e})
    except RuntimeError as e:
        Logger.error(e)
        await send_embedded_message(ctx, 0xFF0000, {"title": "ERROR", "desc": e})
    except Exception as e:
        Logger.error(e)
        await send_embedded_message(
            ctx,
            0xFF0000,
            {
                "title": "ERROR",
                "desc": "An error occurred. Command will be ignored.",
            },
        )
