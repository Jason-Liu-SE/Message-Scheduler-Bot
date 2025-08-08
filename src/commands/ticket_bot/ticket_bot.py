import discord
from discord.ext import commands
from discord.ext.commands.bot import Bot
from discord import app_commands

from commands.ticket_bot.ticket_bot_rewards import TicketBotRewards
from commands.ticket_bot.ticket_bot_trade import TicketBotTrade
from helpers.command_helper import *
from helpers.id_helpers import *
from helpers.message_utils import *
from helpers.ticket_bot.mongo_utils import *
from helpers.time import *
from helpers.validate import *


class TicketBot(
    commands.GroupCog, group_name="ticket", group_description="Manage your tickets"
):
    __allowed_roles = [807335525798117407, "@everyone"]

    def __init__(self, bot: Bot) -> None:
        self.__bot = bot
        self.trade.bot = bot
        self.rewards.bot = bot

    ####################################################################################
    ################################### GROUPS #########################################
    ####################################################################################
    trade = TicketBotTrade(
        name="trade",
        description="Manage ticket trading",
        allowed_roles=__allowed_roles,
    )
    rewards = TicketBotRewards(
        name="rewards",
        description="Interact with the rewards system",
        allowed_roles=__allowed_roles,
    )

    ####################################################################################
    ################################### COMMANDS #######################################
    ####################################################################################
    @app_commands.command(
        name="leaderboard", description="Displays a leaderboard with all users' tickets"
    )
    async def leaderboard(self, interaction: discord.Interaction):
        await handle_command(self.handle_leaderboard, interaction, self.__allowed_roles)

    @app_commands.command(name="view", description="View a user's tickets")
    @app_commands.describe(user="Target user")
    async def view(self, interaction: discord.Interaction, user: discord.Member):
        await handle_command(self.handle_view, interaction, self.__allowed_roles, user)

    @app_commands.command(
        name="help", description="List more info about Ticket Bot commands"
    )
    async def help(self, interaction: discord.Interaction):
        await handle_command(self.handle_help, interaction, self.__allowed_roles)

    ####################################################################################
    ################################### HANDLERS #######################################
    ####################################################################################
    async def handle_leaderboard(self, interaction: discord.Interaction) -> None:
        try:
            user_objs = await get_ranked_user_objects("tickets", "DESC", limit=50)
        except Exception as e:
            Logger.exception(e)
            await send_error(
                interaction, f"An error occurred while creating the leaderboard"
            )
            return

        if len(user_objs) == 0:
            await send_embedded_message(
                interaction,
                colour=Colour.YELLOW,
                title="Leaderboard",
                desc="No one has tickets yet!",
            )
            return

        # creating leaderboard
        ranks = ""
        names = ""
        tickets = ""

        for index, user_obj in enumerate(user_objs.items()):
            user_id = user_obj[0]
            user_info = user_obj[1]
            user = interaction.guild.get_member(user_id)

            ranks += f"{index + 1}{"" if index + 1 >= len(user_objs) else "\n"}"
            names += f"{user.display_name}{"" if index + 1 >= len(user_objs) else "\n"}"
            tickets += (
                f"{user_info["tickets"]}{"" if index + 1 >= len(user_objs) else "\n"}"
            )

        await send_embedded_message(
            interaction,
            colour=Colour.MINT,
            title=f"{"Top 50 " if len(user_objs) >= 50 else ""}Leaderboard",
            desc=None,
            fields=[
                {"name": "Rank", "value": ranks, "inline": True},
                {"name": "Name", "value": names, "inline": True},
                {"name": "Tickets", "value": tickets, "inline": True},
            ],
        )

    async def handle_view(
        self, interaction: discord.Interaction, user: discord.Member
    ) -> None:
        try:
            user_obj = await get_user_object(user.id)

            if not user_obj:
                raise ValueError(f"User with id {user.id} does not exist in records")
        except ValueError as e:
            Logger.warn(e)
            await send_error(
                interaction, f"Could not retrieve {user.display_name}'s tickets"
            )
            return
        except Exception as e:
            Logger.exception(e)
            await send_error(
                interaction, f"Could not retrieve {user.display_name}'s tickets"
            )
            return

        await send_embedded_message(
            interaction,
            colour=Colour.GREEN,
            title=f"{user.display_name}'s Tickets",
            desc=f"{user_obj["tickets"]}",
        )

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
