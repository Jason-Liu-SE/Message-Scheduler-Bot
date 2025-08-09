from random import randint
import discord
from discord import app_commands

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
from ui.ticket_bot.ternary_action import TernaryActionView


class TicketBotTrade(app_commands.Group):
    __TRADE_TIMEOUT = 300

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
        trade_id = ObjectId()
        instigator_user = interaction.user

        confirmations = {instigator_user.id: False, target_user.id: False}

        # Input verification
        if target_user.id == instigator_user.id:
            raise ValueError("You cannot start a trade with yourself")

        if wager < 1:
            raise ValueError("Wager must be greater than 0")

        user_objs = await verify_trade_users(
            instigator_user=instigator_user, target_user=target_user, tickets=wager
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
                desc=create_coinflip_msg(
                    confirmations[instigator_user.id], confirmations[target_user.id]
                ),
                is_successful=False,
            )
            await send_success(
                interaction,
                f"Successfully cancelled trade request `id: {trade_id}` between {instigator_user.mention} and {target_user.mention}.",
                title="Trade Cancelled",
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
                desc=create_coinflip_msg(
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
                desc=create_coinflip_msg(
                    confirmations[instigator_user.id], confirmations[target_user.id]
                ),
            )

            # Attempt to complete coinflip
            if confirmations[instigator_user.id] and confirmations[target_user.id]:
                await view.disable_children()
                view.timeout = 15

                target_user_init_tickets = user_objs[target_user.id]["tickets"]
                instigator_user_init_tickets = user_objs[instigator_user.id]["tickets"]

                has_error = False

                try:
                    is_target_winner = randint(1, 100) > 50
                    await complete_trade(
                        instigator_user=instigator_user,
                        target_user=target_user,
                        tickets=wager,
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
                        f"Could not complete trade `id: {trade_id}` between {instigator_user.mention} and {target_user.mention}",
                        e,
                    )
                else:
                    # Handle successful trade completion
                    message_errors = 0

                    try:
                        await update_trade_msg(
                            view=view,
                            msg_embed_ref=trade_embed,
                            desc=create_coinflip_msg(
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
                        await send_success(
                            interaction,
                            f"### Winnner: {target_user.mention if is_target_winner else instigator_user.mention}\n"
                            + f">>> Successfully completed the coinflip with `id: {trade_id}` between {instigator_user.mention} and {target_user.mention}.",
                            title="Coinflip Completed",
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
                            f"Reverted trade id: `{trade_id}` between `{target_user.name}` and `{instigator_user.name}`"
                        )

                if has_error:
                    await update_trade_msg(
                        view=view,
                        msg_embed_ref=trade_embed,
                        desc=create_coinflip_msg(
                            confirmations[instigator_user.id],
                            confirmations[target_user.id],
                        ),
                        is_successful=False,
                    )

        def create_coinflip_msg(
            instigator_ready: bool, target_ready: bool, winner: str = ""
        ) -> str:
            winner_msg = "" if len(winner) == 0 else f"**Winner**: {winner}\n"

            return (
                f"-# Trade ID: {trade_id}\n\n{instigator_user.mention} would like to coinflip trade with {target_user.mention}!\n\n"
                + f"**Tickets wagered**: `{wager}`\n{winner_msg}"
                + f"### Confirmations ({self.__TRADE_TIMEOUT // 60}m timeout):\n>>> "
                + f"{display_confirmation(instigator_ready)} {instigator_user.mention}\n{display_confirmation(target_ready)} {target_user.mention}"
            )

        # creating a coinflip interaction
        coinflip_view = TernaryActionView(
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
            title="Coinflip Trade",
            desc=create_coinflip_msg(
                confirmations[instigator_user.id], confirmations[target_user.id]
            ),
            colour=Colour.YELLOW,
        )
        await send_existing_embedded_message(
            interaction, embed=trade_embed, view=coinflip_view
        )
        coinflip_view.msg_ref = await interaction.original_response()
