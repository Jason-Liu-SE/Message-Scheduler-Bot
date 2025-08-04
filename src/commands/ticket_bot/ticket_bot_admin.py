import discord
from discord.ext import commands
from discord.ext.commands.bot import Bot
from discord import app_commands

from helpers.command_helper import *
from helpers.id_helpers import *
from helpers.message_utils import *
from helpers.time import *
from helpers.validate import *


class TicketBotAdmin(
    commands.GroupCog, group_name="ticketadmin", group_description="Manage your tickets"
):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

        self.__allowed_roles = [
            807340774781878333,
            838169320461697085,
            "👁‍🗨 Head Moderator 👁‍🗨",
            "Administrator",
            "Admin",
        ]

    ####################################################################################
    ################################ AUTOCOMPLETE ######################################
    ####################################################################################

    ####################################################################################
    ################################### COMMANDS #######################################
    ####################################################################################
    @app_commands.command(name="add", description="Adds tickets to a user")
    async def add(self, interaction: discord.Interaction):
        await handle_command(self.handle_add, interaction, self.__allowed_roles)

    @app_commands.command(name="remove", description="Remove tickets from a user")
    async def remove(self, interaction: discord.Interaction):
        await handle_command(self.handle_remove, interaction, self.__allowed_roles)

    @app_commands.command(name="set", description="Sets a user's tickets")
    async def set(self, interaction: discord.Interaction):
        await handle_command(self.handle_set, interaction, self.__allowed_roles)

    @app_commands.command(
        name="help", description="List more info about the Admin Ticket Bot commands"
    )
    async def help(self, interaction: discord.Interaction):
        await handle_command(self.handle_help, interaction, self.__allowed_roles)

    ####################################################################################
    ################################### HANDLERS #######################################
    ####################################################################################
    async def handle_add(self, interaction: discord.Interaction) -> None:
        pass

    async def handle_remove(self, interaction: discord.Interaction) -> None:
        pass

    async def handle_set(self, interaction: discord.Interaction) -> None:
        pass

    async def handle_help(self, interaction: discord.Interaction) -> None:
        pass


# automatically ran when using load_extensions
async def setup(bot: Bot) -> None:
    # registers cog
    if is_development():
        await bot.add_cog(
            TicketBotAdmin(bot),
            guild=discord.Object(id=int(os.environ["TEST_DISCORD_SERVER"])),
        )
    else:
        await bot.add_cog(TicketBotAdmin(bot))
