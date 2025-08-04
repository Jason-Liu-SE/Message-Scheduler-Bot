import discord
from discord.ext import commands
from discord.ext.commands.bot import Bot
from discord import app_commands

from helpers.command_helper import *
from helpers.id_helpers import *
from helpers.message_utils import *
from helpers.time import *
from helpers.validate import *


class TicketBot(
    commands.GroupCog, group_name="ticket", group_description="Manage your tickets"
):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

        self.__allowed_roles = [807335525798117407, "Everyone"]

    ####################################################################################
    ################################### GROUPS #########################################
    ####################################################################################
    trade = app_commands.Group(name="trade", description="Manage ticket trading")

    ####################################################################################
    ################################ AUTOCOMPLETE ######################################
    ####################################################################################

    ####################################################################################
    ################################### COMMANDS #######################################
    ####################################################################################
    @app_commands.command(
        name="leaderboard", description="Displays a leaderboard with user's tickets"
    )
    async def leaderboard(self, interaction: discord.Interaction):
        await handle_command(self.handle_leaderboard, interaction, self.__allowed_roles)

    @app_commands.command(name="view", description="View a user's tickets")
    async def view(self, interaction: discord.Interaction):
        await handle_command(self.handle_view, interaction, self.__allowed_roles)

    @app_commands.command(name="redeem", description="Redeem items for tickets")
    async def redeem(self, interaction: discord.Interaction):
        await handle_command(self.handle_redeem, interaction, self.__allowed_roles)

    @trade.command(name="accept", description="Accept a user's trade request")
    async def trade_accept(self, interaction: discord.Interaction):
        await handle_command(
            self.handle_trade_accept, interaction, self.__allowed_roles
        )

    @trade.command(name="reject", description="Reject a user's trade request")
    async def trade_reject(self, interaction: discord.Interaction):
        await handle_command(
            self.handle_trade_reject, interaction, self.__allowed_roles
        )

    @trade.command(name="start", description="Request to trade with another user")
    async def trade_start(self, interaction: discord.Interaction):
        await handle_command(self.handle_trade_start, interaction, self.__allowed_roles)

    @trade.command(
        name="coinflip", description="Coinflip for tickets with another user"
    )
    async def trade_coinflip(self, interaction: discord.Interaction):
        await handle_command(
            self.handle_trade_coinflip, interaction, self.__allowed_roles
        )

    @app_commands.command(
        name="help", description="List more info about Ticket Bot commands"
    )
    async def help(self, interaction: discord.Interaction):
        await handle_command(self.handle_help, interaction, self.__allowed_roles)

    ####################################################################################
    ################################### HANDLERS #######################################
    ####################################################################################
    async def handle_leaderboard(self, interaction: discord.Interaction) -> None:
        pass

    async def handle_view(self, interaction: discord.Interaction) -> None:
        pass

    async def handle_redeem(self, interaction: discord.Interaction) -> None:
        pass

    async def handle_trade_accept(self, interaction: discord.Interaction) -> None:
        pass

    async def handle_trade_reject(self, interaction: discord.Interaction) -> None:
        pass

    async def handle_trade_start(self, interaction: discord.Interaction) -> None:
        pass

    async def handle_trade_coinflip(self, interaction: discord.Interaction) -> None:
        pass

    async def handle_help(self, interaction: discord.Interaction) -> None:
        pass


# automatically ran when using load_extensions
async def setup(bot: Bot) -> None:
    # registers cog
    if is_development():
        await bot.add_cog(
            TicketBot(bot),
            guild=discord.Object(id=int(os.environ["TEST_DISCORD_SERVER"])),
        )
    else:
        await bot.add_cog(TicketBot(bot))
