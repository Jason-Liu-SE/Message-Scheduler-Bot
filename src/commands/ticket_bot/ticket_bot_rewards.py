import discord
from discord import app_commands

from helpers.command_helper import *
from helpers.id_helpers import *
from helpers.message_utils import *
from helpers.ticket_bot.mongo_utils import *
from helpers.time import *
from helpers.validate import *


class TicketBotRewards(app_commands.Group):
    def __init__(self, name: str, description: str, allowed_roles: list) -> None:
        super().__init__(name=name, description=description)
        self.__allowed_roles = allowed_roles

    ####################################################################################
    ################################ AUTOCOMPLETE ######################################
    ####################################################################################

    ####################################################################################
    ################################### COMMANDS #######################################
    ####################################################################################
    @app_commands.command(
        name="list",
        description="View the different things you can redeem tickets for",
    )
    @app_commands.describe(page="The rewards page. Default = 1")
    async def list(self, interaction: discord.Interaction, page: int = 1):
        await handle_command(self.handle_list, interaction, self.__allowed_roles, page)

    @app_commands.command(name="inspect", description="View more about a reward")
    async def inspect(self, interaction: discord.Interaction):
        await handle_command(self.handle_inspect, interaction, self.__allowed_roles)

    @app_commands.command(name="redeem", description="Redeem items for tickets")
    async def redeem(self, interaction: discord.Interaction):
        await handle_command(self.handle_redeem, interaction, self.__allowed_roles)

    @app_commands.command(
        name="help", description="List more info about Ticket Bot commands"
    )
    async def help(self, interaction: discord.Interaction):
        await handle_command(self.handle_help, interaction, self.__allowed_roles)

    ####################################################################################
    ################################### HANDLERS #######################################
    ####################################################################################
    async def handle_list(self, interaction: discord.Interaction, page: int) -> None:
        pass

    async def handle_inspect(self, interaction: discord.Interaction) -> None:
        pass

    async def handle_redeem(self, interaction: discord.Interaction) -> None:
        pass

    async def handle_help(self, interaction: discord.Interaction) -> None:
        pass
