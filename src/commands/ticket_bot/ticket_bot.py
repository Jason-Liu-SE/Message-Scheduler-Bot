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
        help_desc = (
            "The Ticket bot is used to interact with, and use your tickets."
            + f"\n\n### The commands are as follows:"
        )

        leaderboard_msg = (
            "Lists a ranking of users based on how many tickets they have. If someone isn't listed on the leaderboard, "
            + f"it probably means that they don't exist in the ticket system yet.\n"
            + f">>> Format: `/ticket leaderboard`"
        )

        balance_msg = (
            "Shows how many tickets you have.\n" + f">>> Format: `/ticket balance`"
        )

        view_msg = (
            "Allows you to view another player's tickets.\n\n"
            + f"**Fields**:\n"
            + f"`user`: a user to view. Fill via autocomplete.\n"
            + f">>> Format: `/ticket view <user>`\n\n"
            + f"E.g. **/ticket view @user**\nThis would display @user's tickets"
        )

        rewards_list_msg = (
            "This lists all the rewards that can be claimed.\n\n"
            + f"**Fields**:\n"
            + f"`page`: the desired page to view. Default=1, must be >0.\n"
            + f">>> Format: `/ticket rewards list <*optional*:page>`\n\n"
            + f"E.g. **/ticket rewards list `page:`2**\nThis would display the 2nd page of the reward list."
        )

        rewards_inspect_msg = (
            "This shows more information about a particular reward.\n\n"
            + f"**Fields**:\n"
            + f"`item`: desired reward. The `reward ID` can be found on the `/ticket rewards list`, or via autocomplete.\n"
            + f">>> Format: `/ticket rewards inspect <reward>`\n\n"
            + f"E.g. **/ticket rewards inspect 97979f9175a4b91f17d8a472**\nThis would display more information about the reward corresponding to 97979f9175a4b91f17d8a472."
        )

        rewards_redeem_msg = (
            "This allows you to redeem one of the rewards on the `/ticket rewards list` list. To redeem an item, type the `reward ID` of the reward into the `item` "
            + f"field. You can find this value on the `/ticket rewards list` list, and/or use the autocomplete dropdown.\n\n"
            + f"Note that you'll need to confirm your transaction before it goes through. Once confirmed, please wait patiently "
            + f"for your order to be fullfilled by an admin/moderator.\n"
            + f">>> Format: `/ticket rewards redeem <item>`\n\n"
            + f"E.g. **/ticket rewards redeem 97979f9175a4b91f17d8a472**\nThis would start the redemption process for the reward corresponding to 97979f9175a4b91f17d8a472."
        )

        trade_start_msg = (
            "This starts a trade request with another user.\n\n"
            + f"**Fields**:\n"
            + f"`target`: The user that you'd like to trade with. Use the autocomplete to fill this.\n"
            + f"`action`: The trade action. Either `send` (send tickets to `target`) or `request` (get tickets from `target`).\n"
            + f"`tickets`: The number of tickets to trade. Must be > 0.\n\n"
            + f"Once you submit the command, you'll need to `ready`-up for the trade. Once all parties in the trade are `ready`, the trade will proceed. "
            + f"If either user wants to cancel the trade, they may press the `cancel` button. Alternatively, if `5 minutes` passes and the trade isn't completed, it cancels.\n"
            + f">>> Format: `/ticket trade start <target> <action> <tickets>`\n\n"
            + f"E.g. **/ticket trade start @user send 5**\n"
            + f"This would start a trade with @user, which if accepted by both parties, would transfer `5 tickets` from the `trade initiator` to @user."
        )

        trade_coinflip_msg = (
            "This starts a coinflip trade with another user. Each user has a 50% chance to win.\n\n"
            + f"**Fields**:\n"
            + f"`target`: the target user to start a coinflip trade with.\n"
            + f"`wager`: the number of tickets that the winner should get and the loser should lose. Must be > 0.\n"
            + f">>> Format: `/ticket trade coinflip <target> <wager>`\n\n"
            + f"E.g. **/ticket trade coinflip @user 5**\nThis would start a coinflip trade with @user. If @user won, they would get `5 tickets` and the `trade initiator` would lose `5 ticket`."
        )

        fields = [
            {"name": "[1] leaderboard", "value": leaderboard_msg},
            {"name": "[2] balance", "value": balance_msg},
            {"name": "[3] view", "value": view_msg},
            {"name": "[4] rewards list", "value": rewards_list_msg},
            {"name": "[5] rewards inspect", "value": rewards_inspect_msg},
            {"name": "[6] rewards redeem", "value": rewards_redeem_msg},
            {"name": "[7] trade start", "value": trade_start_msg},
            {"name": "[8] trade coinflip", "value": trade_coinflip_msg},
        ]

        await send_embedded_message(
            interaction,
            colour=Colour.PURPLE,
            title="Ticket Commands",
            desc=help_desc,
            fields=fields,
        )


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
