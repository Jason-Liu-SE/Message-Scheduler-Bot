import discord
from discord import app_commands

from helpers.command_helper import *
from helpers.id_helpers import *
from helpers.message_utils import *
from helpers.ticket_bot.mongo_utils import *
from helpers.time import *
from helpers.validate import *


class TicketBotTrade(app_commands.Group):
    def __init__(self, name: str, description: str, allowed_roles: list) -> None:
        super().__init__(name=name, description=description)
        self.__allowed_roles = allowed_roles

    ####################################################################################
    ################################ AUTOCOMPLETE ######################################
    ####################################################################################

    ####################################################################################
    ################################### COMMANDS #######################################
    ####################################################################################
    @app_commands.command(name="accept", description="Accept a user's trade request")
    async def accept(self, interaction: discord.Interaction):
        await handle_command(self.handle_accept, interaction, self.__allowed_roles)

    @app_commands.command(name="reject", description="Reject a user's trade request")
    async def reject(self, interaction: discord.Interaction):
        await handle_command(self.handle_reject, interaction, self.__allowed_roles)

    @app_commands.command(
        name="cancel", description="Cancels an existing trade request"
    )
    async def cancel(self, interaction: discord.Interaction):
        await handle_command(self.handle_cancel, interaction, self.__allowed_roles)

    @app_commands.command(
        name="start", description="Request to trade with another user"
    )
    async def start(self, interaction: discord.Interaction):
        await handle_command(self.handle_start, interaction, self.__allowed_roles)

    @app_commands.command(
        name="coinflip", description="Coinflip for tickets with another user"
    )
    async def coinflip(self, interaction: discord.Interaction):
        await handle_command(self.handle_coinflip, interaction, self.__allowed_roles)

    ####################################################################################
    ################################### HANDLERS #######################################
    ####################################################################################
    async def handle_accept(self, interaction: discord.Interaction) -> None:
        pass

    async def handle_reject(self, interaction: discord.Interaction) -> None:
        pass

    async def handle_cancel(self, interaction: discord.Interaction) -> None:
        pass

    async def handle_start(self, interaction: discord.Interaction) -> None:
        pass

    async def handle_coinflip(self, interaction: discord.Interaction) -> None:
        pass
