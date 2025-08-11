from random import randint
import discord
from discord import app_commands

from commands.command_bot import CommandBot
from helpers.command_helper import *
from helpers.exception_helpers import handle_error
from helpers.id_helpers import *
from helpers.message_utils import *
from helpers.ticket_bot.mongo_utils import *
from helpers.ticket_bot.trade_helpers import (
    complete_trade,
    display_confirmation,
    update_confirmation_state,
    update_trade_msg,
    verify_trade_users,
)
from helpers.time import *
from helpers.validate import *
from ui.common.ternary_action import TernaryActionView


class TicketBotTrade(app_commands.Group, CommandBot):
    __TRADE_TIMEOUT = 300

    def __init__(self, name: str, description: str, allowed_roles: list) -> None:
        super().__init__(name=name, description=description)
        self._allowed_roles = allowed_roles
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
    @app_commands.describe(
        target="The player to start a trade with",
        action="Whether to 'send' or 'request' tickets to/from the target",
        tickets="The number of tickets to send/receive to/from the target",
    )
    @enrich_command
    async def start(
        self,
        interaction: discord.Interaction,
        target: discord.Member,
        action: Literal["send", "request"],
        tickets: app_commands.Range[int, 1],
    ):
        await self.handle_start(
            interaction,
            target_user=target,
            action=action,
            tickets=tickets,
        )

    @app_commands.command(
        name="coinflip", description="Coinflip for tickets with another user"
    )
    @app_commands.describe(
        target="The player to start a coinflip with",
        wager="The number of tickets that the loser of the coinflip will give to the winner of the coinflip",
    )
    @enrich_command
    async def coinflip(
        self,
        interaction: discord.Interaction,
        target: discord.Member,
        wager: app_commands.Range[int, 1],
    ):
        await self.handle_coinflip(interaction, target_user=target, wager=wager)

    ####################################################################################
    ################################### HANDLERS #######################################
    ####################################################################################
    async def handle_start(
        self,
        interaction: discord.Interaction,
        target_user: discord.Member,
        action: Literal["send", "request"],
        tickets: app_commands.Range[int, 1],
    ) -> None:
        async def get_ticket_winner() -> Literal["instigator", "target"]:
            return "target" if action == "send" else "instigator"

        await self.handle_trade(
            interaction,
            target_user=target_user,
            tickets=tickets,
            trade_action="➡️ Send" if action == "send" else "⬅️ Request",
            flow_emoji="➡️" if action == "send" else "⬅️",
            win_label="Ticket recipient",
            get_ticket_winner=get_ticket_winner,
        )

    async def handle_coinflip(
        self, interaction: discord.Interaction, target_user: discord.Member, wager: int
    ) -> None:
        async def get_ticket_winner() -> Literal["instigator", "target"]:
            return "target" if randint(0, 1) == 0 else "instigator"

        await self.handle_trade(
            interaction,
            target_user=target_user,
            tickets=wager,
            trade_action="🎲 Coinflip",
            flow_emoji="⬅️❓➡️",
            win_label="Winner",
            get_ticket_winner=get_ticket_winner,
        )

    async def handle_trade(
        self,
        interaction: discord.Interaction,
        target_user: discord.Member,
        tickets: int,
        trade_action: str,
        flow_emoji: str,  # the direction that tickets will flow
        win_label: str,
        get_ticket_winner: Callable[..., Awaitable[Literal["instigator", "target"]]],
    ) -> None:
        trade_id = ObjectId()
        instigator_user = interaction.user

        confirmations = {instigator_user.id: False, target_user.id: False}

        # Input verification
        if target_user.id == instigator_user.id:
            raise ValueError("You cannot start a trade with yourself")

        if tickets < 1:
            raise ValueError("Tickets traded must be greater than 0")

        user_objs = await verify_trade_users(
            instigator_user=instigator_user, target_user=target_user, tickets=tickets
        )

        # User event handlers
        async def on_cancel(
            interaction: discord.Interaction,
            view: TernaryActionView,
            btn: discord.ui.Button,
        ) -> None:
            await view.disable_children()
            view.timeout = 15

            await update_trade_msg(
                view=view,
                msg_embed_ref=trade_embed,
                desc=create_trade_msg(
                    confirmations[instigator_user.id], confirmations[target_user.id]
                ),
                is_successful=False,
            )
            await send_success(
                interaction,
                f"Successfully cancelled **`{trade_action.upper()}`** trade request `id: {trade_id}` between {instigator_user.mention} and {target_user.mention}.",
                title=f"{trade_action.title()} Trade Cancelled",
            )

        async def on_unready(
            interaction: discord.Interaction,
            view: TernaryActionView,
            btn: discord.ui.Button,
        ) -> None:
            update_confirmation_state(
                interaction.user.id, confirmation_states=confirmations, new_state=False
            )
            await update_trade_msg(
                view=view,
                msg_embed_ref=trade_embed,
                desc=create_trade_msg(
                    confirmations[instigator_user.id], confirmations[target_user.id]
                ),
            )

        async def on_ready(
            interaction: discord.Interaction,
            view: TernaryActionView,
            btn: discord.ui.Button,
        ) -> None:
            update_confirmation_state(
                interaction.user.id, confirmation_states=confirmations, new_state=True
            )
            await update_trade_msg(
                view=view,
                msg_embed_ref=trade_embed,
                desc=create_trade_msg(
                    confirmations[instigator_user.id], confirmations[target_user.id]
                ),
            )

            # Attempt to complete trade
            if confirmations[instigator_user.id] and confirmations[target_user.id]:
                await view.disable_children()
                view.timeout = 15

                target_user_init_tickets = user_objs[target_user.id]["tickets"]
                instigator_user_init_tickets = user_objs[instigator_user.id]["tickets"]

                has_error = False

                try:
                    is_target_winner = await get_ticket_winner() == "target"
                    await complete_trade(
                        instigator_user=instigator_user,
                        target_user=target_user,
                        tickets=tickets,
                        send_direction=(
                            "instigator_to_target"
                            if is_target_winner
                            else "target_to_instigator"
                        ),
                    )
                except ValueError as e:
                    has_error = True
                    await handle_error(
                        interaction,
                        e,
                        None,
                    )
                except Exception as e:
                    has_error = True
                    await handle_error(
                        interaction,
                        f"Could not complete **`{trade_action.upper()}`** trade `id: {trade_id}` between {instigator_user.mention} and {target_user.mention}",
                        e,
                    )
                else:
                    # Handle successful trade completion
                    message_errors = 0

                    try:
                        await update_trade_msg(
                            view=view,
                            msg_embed_ref=trade_embed,
                            desc=create_trade_msg(
                                confirmations[instigator_user.id],
                                confirmations[target_user.id],
                                winner=(
                                    target_user.mention
                                    if is_target_winner
                                    else instigator_user.mention
                                ),
                            ),
                            is_successful=True,
                        )
                    except Exception as e:
                        message_errors += 1
                        Logger.error(e)

                    try:
                        invert = 1 if is_target_winner else -1
                        await send_success(
                            interaction,
                            f"### {win_label}: {target_user.mention if is_target_winner else instigator_user.mention}\n"
                            + f"{instigator_user.mention} now has `{instigator_user_init_tickets - tickets * invert}` tickets.\n"
                            + f"{target_user.mention} now has `{target_user_init_tickets + tickets * invert}` tickets.\n\n"
                            + f">>> Completes **`{trade_action.upper()}`** trade `id: {trade_id}` between {instigator_user.mention} and {target_user.mention}.",
                            title=f"{trade_action.title()} Trade Completed",
                        )
                    except Exception as e:
                        message_errors += 1
                        Logger.error(e)

                    # Revert trade if both attempt to inform users of the trade outcome fail
                    if message_errors == 2:
                        user_objs[target_user.id]["tickets"] = target_user_init_tickets
                        user_objs[instigator_user.id][
                            "tickets"
                        ] = instigator_user_init_tickets

                        await update_user_objects(user_objs)

                        Logger.info(
                            f"Reverted **`{trade_action.upper()}`** trade id: `{trade_id}` between `{target_user.name}` and `{instigator_user.name}`"
                        )

                if has_error:
                    await update_trade_msg(
                        view=view,
                        msg_embed_ref=trade_embed,
                        desc=create_trade_msg(
                            confirmations[instigator_user.id],
                            confirmations[target_user.id],
                        ),
                        is_successful=False,
                    )

        def create_trade_msg(
            instigator_ready: bool, target_ready: bool, winner: str = ""
        ) -> str:
            winner_msg = "" if len(winner) == 0 else f"**{win_label}**: {winner}\n"

            return (
                f"-# Trade ID: {trade_id}\n\n{instigator_user.mention} would like to **`{trade_action.upper()}`** trade with {target_user.mention}!\n\n"
                + f"**Tickets in trade**: `{tickets}`\n**Ticket flow**: {instigator_user.mention} {flow_emoji} {target_user.mention}\n{winner_msg}"
                + f"### Confirmations ({self.__TRADE_TIMEOUT // 60}m timeout):\n>>> "
                + f"{display_confirmation(instigator_ready)} {instigator_user.mention}\n{display_confirmation(target_ready)} {target_user.mention}"
            )

        # creating a trade interaction
        trade_view = TernaryActionView(
            primary_label="Ready",
            secondary_label="Un-ready",
            danger_label="Cancel",
            primary_cb=on_ready,
            secondary_cb=on_unready,
            danger_cb=on_cancel,
            authorized_ids=[instigator_user.id, target_user.id],
            timeout=self.__TRADE_TIMEOUT,
        )
        trade_embed = generate_embedded_message(
            title=f"{trade_action.title()} Trade",
            desc=create_trade_msg(
                confirmations[instigator_user.id], confirmations[target_user.id]
            ),
            colour=Colour.YELLOW,
        )
        await send_existing_embedded_message(
            interaction, embed=trade_embed, view=trade_view
        )
        trade_view.msg_ref = await interaction.original_response()
