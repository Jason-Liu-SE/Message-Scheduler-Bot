from random import randint
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
        self.bot = None  # set by the parent

    ####################################################################################
    ################################ AUTOCOMPLETE ######################################
    ####################################################################################

    ####################################################################################
    ################################### COMMANDS #######################################
    ####################################################################################
    @app_commands.command(
        name="start", description="Request to trade with another user"
    )
    async def start(self, interaction: discord.Interaction):
        await handle_command(self.handle_start, interaction, self.__allowed_roles)

    @app_commands.command(
        name="coinflip", description="Coinflip for tickets with another user"
    )
    @app_commands.describe(
        target="The player to start a coinflip with",
        wager="The number of tickets that the loser of the coinflip will give to the winner of the coinflip",
    )
    async def coinflip(
        self,
        interaction: discord.Interaction,
        target: discord.Member,
        wager: app_commands.Range[int, 1],
    ):
        await handle_command(
            self.handle_coinflip, interaction, self.__allowed_roles, target, wager
        )

    ####################################################################################
    ################################### HANDLERS #######################################
    ####################################################################################
    async def handle_start(self, interaction: discord.Interaction) -> None:
        pass

    async def handle_coinflip(
        self, interaction: discord.Interaction, target_user: discord.Member, wager: int
    ) -> None:
        if wager < 1:
            raise ValueError("Wager must be greater than 0")

        # Determining coinflip winner
        target_is_winner = False

        if randint(1, 100) > 50:
            target_is_winner = True
