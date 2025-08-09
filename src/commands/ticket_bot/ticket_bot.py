import discord
from discord.ext import commands
from discord.ext.commands.bot import Bot
from discord import app_commands

from commands.command_bot import CommandBot
from commands.ticket_bot.ticket_bot_rewards import TicketBotRewards
from commands.ticket_bot.ticket_bot_trade import TicketBotTrade
from helpers.command_helper import *
from helpers.id_helpers import *
from helpers.message_utils import *
from helpers.ticket_bot.mongo_utils import *
from helpers.time import *
from helpers.validate import *


class TicketBot(
    commands.GroupCog,
    CommandBot,
    group_name="ticket",
    group_description="Manage your tickets",
):
    _allowed_roles = [807335525798117407, "@everyone"]

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
        allowed_roles=_allowed_roles,
    )
    rewards = TicketBotRewards(
        name="rewards",
        description="Interact with the rewards system",
        allowed_roles=_allowed_roles,
    )

    ####################################################################################
    ################################### COMMANDS #######################################
    ####################################################################################
    @app_commands.command(
        name="leaderboard", description="Displays a leaderboard with all users' tickets"
    )
    @enrich_command
    async def leaderboard(self, interaction: discord.Interaction):
        await self.handle_leaderboard(interaction)

    @app_commands.command(name="balance", description="View your balance")
    @enrich_command
    async def balance(self, interaction: discord.Interaction):
        await self.handle_balance(interaction)

    @app_commands.command(name="view", description="View a user's tickets")
    @app_commands.describe(user="Target user")
    @enrich_command
    async def view(self, interaction: discord.Interaction, user: discord.Member):
        await self.handle_view(interaction, user=user)

    @app_commands.command(
        name="help", description="List more info about Ticket Bot commands"
    )
    @enrich_command
    async def help(self, interaction: discord.Interaction):
        await self.handle_help(interaction)

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
        fields = []

        for index, user_obj in enumerate(user_objs.items()):
            user_id = user_obj[0]
            user_info = user_obj[1]
            user = interaction.guild.get_member(user_id)

            fields.append(
                {
                    "name": (
                        f"#{index + 1}\t{user.display_name} "
                        + (
                            ":first_place:"
                            if index == 0
                            else (
                                ":second_place:"
                                if index == 1
                                else ":third_place:" if index == 2 else ""
                            )
                        )
                    ),
                    "value": f"> **{user_info["tickets"]}** tickets",
                }
            )

        await send_embedded_message(
            interaction,
            colour=Colour.MINT,
            title=f"{"Top 50 " if len(user_objs) >= 50 else ""}Ticket Leaderboard",
            desc=None,
            fields=fields,
        )

    async def handle_balance(self, interaction: discord.Interaction) -> None:
        user = interaction.user

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
            colour=user.colour,
            title=f"{user.display_name}'s Tickets",
            desc=f"{user_obj["tickets"]}",
            thumbnail=user.display_avatar.url,
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
            colour=user.color,
            title=f"{user.display_name}'s Tickets",
            desc=f"{user_obj["tickets"]}",
            thumbnail=user.display_avatar.url,
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
