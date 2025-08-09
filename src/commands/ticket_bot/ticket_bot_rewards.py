from math import ceil
import discord
from discord import app_commands

from helpers.command_helper import *
from helpers.exception_helpers import handle_error
from helpers.id_helpers import *
from helpers.message_utils import *
from helpers.ticket_bot.autofill_helpers import *
from helpers.ticket_bot.format_helpers import display_stock
from helpers.ticket_bot.mongo_utils import *
from helpers.time import *
from helpers.validate import *

from ui.ticket_bot.confirm_action import ConfirmActionView
from ui.ticket_bot.single_action import SingleActionView


class TicketBotRewards(app_commands.Group):
    __ITEMS_PER_PAGE = 20

    def __init__(self, name: str, description: str, allowed_roles: list) -> None:
        super().__init__(name=name, description=description)
        self.__allowed_roles = allowed_roles
        self.bot: Bot | None = None  # set by the parent

    ####################################################################################
    ################################ AUTOCOMPLETE ######################################
    ####################################################################################
    async def get_pages(interaction: discord.Interaction, current: str) -> int:
        choices = []
        pages = range(
            1, ceil(await count_rewards({}) / TicketBotRewards.__ITEMS_PER_PAGE) + 1
        )

        for page in pages:
            if current.lower() in f"{page}":
                choices.append(app_commands.Choice(name=f"{page}", value=page))

        return choices

    # List
    ac_list_page = generate_autocomplete([], get_pages)

    # Inspect
    ac_inspect_item = generate_autocomplete([], get_reward_choices)

    # Redeem
    ac_redeem_item = generate_autocomplete([], get_reward_choices)

    ####################################################################################
    ################################### COMMANDS #######################################
    ####################################################################################
    @app_commands.command(
        name="list",
        description="View the different things you can redeem tickets for",
    )
    @app_commands.describe(page="The rewards page. Default = 1")
    @app_commands.autocomplete(page=ac_list_page)
    async def list(self, interaction: discord.Interaction, page: int = 1):
        await handle_command(self.handle_list, interaction, self.__allowed_roles, page)

    @app_commands.command(name="inspect", description="View more about a reward")
    @app_commands.describe(item="The ID of the item to be inspected")
    @app_commands.autocomplete(item=ac_inspect_item)
    async def inspect(self, interaction: discord.Interaction, item: str):
        await handle_command(
            self.handle_inspect, interaction, self.__allowed_roles, item
        )

    @app_commands.command(name="redeem", description="Redeem items for tickets")
    @app_commands.describe(item="Item ID to be redeemed")
    @app_commands.autocomplete(item=ac_redeem_item)
    async def redeem(self, interaction: discord.Interaction, item: str):
        await handle_command(
            self.handle_redeem, interaction, self.__allowed_roles, item
        )

    ####################################################################################
    ################################### HANDLERS #######################################
    ####################################################################################
    async def handle_list(self, interaction: discord.Interaction, page: int) -> None:
        num_rewards = await count_rewards({})
        pages = ceil(num_rewards / self.__ITEMS_PER_PAGE)

        page = max(1, min(pages, page))

        skip = (page - 1) * self.__ITEMS_PER_PAGE

        rewards = await get_many_reward_objects(
            {},
            sort_field="name",
            skip=skip,
            limit=self.__ITEMS_PER_PAGE,
        )

        # constructing the listing
        fields = []

        for index, reward in enumerate(rewards.items()):
            desc = f">>> **ID**: {reward[0]}\n**Cost**: {reward[1]["cost"]}\n**Stock**: {display_stock(reward[1]["stock"])}"
            fields.append(
                {"name": f"{index + skip + 1}\t{reward[1]['name']}", "value": desc}
            )

        await send_embedded_message(
            interaction,
            colour=Colour.ORANGE,
            title="Rewards  :shopping_bags:",
            fields=fields,
            footer=f"Page: {page}/{pages}  |  Items {skip + 1}-{skip + len(rewards)} of {num_rewards}",
        )

    async def handle_inspect(self, interaction: discord.Interaction, item: str) -> None:
        if not ObjectId.is_valid(item):
            raise ValueError(f"Item {item} is not valid")

        reward_id = ObjectId(item)

        try:
            reward = await get_reward_object(reward_id)

            if not reward:
                raise Exception
        except Exception as e:
            await handle_error(
                interaction, f"Could not find any rewards with id: {reward_id}", e
            )
            return

        try:
            page_colour = int(reward["page_colour"].split("x")[1], 16)
        except Exception as e:
            page_colour = None
            Logger.error(f"Page colour: '{reward["page_colour"]}' is invalid")

        await send_embedded_message(
            interaction,
            colour=page_colour,
            title=f"Reward | {reward["name"]}",
            desc=f"**ID**: {reward["_id"]}\n**Ticket Cost**: {reward["cost"]}\n**Stock**: {display_stock(reward["stock"])}{f"\n\n{reward["desc"]}" if len(reward["desc"]) > 0 else ""}",
            image=reward["image"] if len(reward["image"]) > 0 else None,
        )

    async def handle_redeem(self, interaction: discord.Interaction, item: str) -> None:
        if not ObjectId.is_valid(item):
            raise ValueError(f"Item {item} is not valid")

        reward_id = ObjectId(item)
        redeemer = interaction.user
        order_id = ObjectId()

        # attempt to order item
        try:
            reward = await get_reward_object(reward_id)

            if not reward:
                raise Exception
        except Exception as e:
            await handle_error(
                interaction, f"Could not find any rewards with id: {reward_id}", e
            )
            return

        if reward["stock"] == 0:
            raise ValueError(f"Reward with id: `{reward_id}` is OUT OF STOCK")

        try:
            user_obj = await get_user_object(redeemer.id)
        except Exception as e:
            handle_error(
                interaction, "There was an issue while retrieving your balance.", e
            )
            return

        if not user_obj:
            raise ValueError(
                "You don't have a balance. Please contact an administrator or moderator."
            )

        if user_obj["tickets"] < reward["cost"]:
            raise ValueError("You don't have enough tickets to purchase this item.")

        async def on_reject(
            interation: discord.Interaction, btn: discord.ui.Button
        ) -> None:
            await send_success(
                interaction,
                f"Successfully cancelled the redemption request for:\n\n"
                + f"**Redeemer**: {redeemer.mention}\n**Order ID**: {order_id}\n**Ticket Cost**: {reward["cost"]}\n**ID**: {reward["_id"]}\n"
                + f"**Name**: {reward["name"]}",
                title="Redemption Cancelled",
            )

        # proceed after confirmation
        async def on_accept(
            interation: discord.Interaction, btn: discord.ui.Button
        ) -> None:
            # update balance
            prev_balance = user_obj["tickets"]
            user_obj["tickets"] -= reward["cost"]

            try:
                await update_user_object(interaction.user.id, user_obj)
            except Exception as e:
                await handle_error(
                    interaction,
                    f"Could not complete redemption process for order id: `{order_id}`",
                    e,
                )
                return

            async def reverse_redemption(prev_balance, prev_stock):
                async def handle_reversal_failure(e: Exception, blame_msg) -> None:
                    err_msg = (
                        f"Failed to reverse redemption of `{reward["_id"]}: {reward["name"]}` for `{reward["cost"]}` tickets by `{interaction.user.name}`. "
                        + f"Expected balance `{prev_balance}`. Expected stock `{prev_stock}`.\n\n"
                        + f"**Redemption Time**: {convert_to_timezone(datetime.now()).strftime("%Y-%m-%d %H:%M:%S")}\n"
                        + f"**Order ID**: {order_id}\n"
                        + f"\n\nCause: {blame_msg}:\n\n {e}"
                    )
                    Logger.error(err_msg)

                    try:
                        admin = interaction.guild.get_member(
                            int(os.environ["REDEEM_TARGET"])
                        )

                        await admin.send(
                            embed=generate_embedded_message(
                                title="ERROR",
                                desc=err_msg,
                                colour=Colour.RED,
                            )
                        )
                    except Exception as e:
                        Logger.error(
                            f"Failed to notify admin of a redemption request reversal for order id: `{order_id}`"
                        )
                        Logger.exception(e)

                try:
                    user_obj["tickets"] = prev_balance
                    await update_user_object(interaction.user.id, user_obj)
                    Logger.info(
                        f"Successfully reversed the user's balance for order id: `{order_id}`"
                    )
                except Exception as e:
                    await handle_reversal_failure(
                        e, f"Could not revert balance for order id: `{order_id}`"
                    )

                try:
                    reward["stock"] = prev_stock
                    await update_reward_object(reward_id, reward)
                    Logger.info(
                        f"Successfully reversed reward stock for order id: `{order_id}`"
                    )
                except Exception as e:
                    await handle_reversal_failure(
                        e, f"Could not revert reward stock for order id: `{order_id}`"
                    )

            # update the stock of the item
            prev_stock = reward["stock"]
            reward["stock"] = (
                reward["stock"] - 1 if reward["stock"] > 0 else reward["stock"]
            )

            try:
                await update_reward_object(reward_id, reward)
            except Exception as e:
                Logger.error("Failed to update reward stock")
                await handle_error(
                    interaction,
                    f"Could not complete redemption process for order id: `{order_id}`",
                    e,
                )
                await reverse_redemption(prev_balance, prev_stock)
                return

            # send redemption message to admin
            try:
                dm_target = interaction.guild.get_member(
                    int(os.environ["REDEEM_TARGET"])
                )

                # mark as read functionality
                async def on_complete(
                    interation: discord.Interaction, btn: discord.ui.Button
                ) -> None:
                    try:
                        edited_embed = generate_embedded_message(
                            title=f"{embed.title}: Completed",
                            desc=embed.description,
                            colour=Colour.GREEN,
                            thumbnail=embed.thumbnail.url,
                        )
                        await order_msg.edit(embed=edited_embed, view=None)
                    except Exception as e:
                        Logger.error(
                            f"Could not mark DM message (order id: {order_id}) as read: {e}"
                        )

                mark_as_complete = SingleActionView(
                    label="Mark as Complete", action_cb=on_complete
                )
                embed = generate_embedded_message(
                    title="Redeem",
                    desc=f"{interaction.user.mention} redeemed:\n\n**ID**: {reward["_id"]}\n**Ticket Cost**: {reward["cost"]}\n**Remaining Stock**: {display_stock(reward["stock"])}\n\n"
                    + f"**Redemption Time**: {convert_to_timezone(datetime.now()).strftime("%Y-%m-%d %H:%M:%S")}\n"
                    + f"**Order ID**: {order_id}\n"
                    + f"**Name**: {reward["name"]}\n\nTheir new balance is `{user_obj["tickets"]}`",
                    colour=Colour.RASPBERRY,
                    thumbnail=interaction.user.display_avatar.url,
                )
                order_msg = await dm_target.send(embed=embed, view=mark_as_complete)
                mark_as_complete.msg_ref = order_msg
            except Exception as e:
                Logger.error("Failed to DM admin")
                await handle_error(
                    interaction,
                    f"Could not complete redemption process for order id: `{order_id}`",
                    e,
                )
                await reverse_redemption(prev_balance, prev_stock)
                return

            # send success message to caller
            try:
                await send_success(
                    interaction,
                    title="Purchase Complete",
                    msg=f"**Order ID**: {order_id}\n\n"
                    + f"Successfully redeemed `{reward["name"]}` for `{reward["cost"]}` tickets\n\n"
                    + f"__**{interaction.user.mention}'s Post-Purchase Summary**__\n**Updated Balance**: `{user_obj["tickets"]}` ticket(s)",
                )
            except Exception as e:
                Logger.error("Failed to send success to redeemer")
                await handle_error(
                    interaction,
                    f"Could not complete redemption process for order id: `{order_id}`",
                    e,
                )
                await order_msg.delete()
                await reverse_redemption(prev_balance, prev_stock)
                return

        # request for confirmation
        confirm = ConfirmActionView(
            accept_cb=on_accept,
            reject_cb=on_reject,
            authorized_ids=[interaction.user.id],
        )
        await send_embedded_message(
            interaction,
            colour=Colour.YELLOW,
            title="Confirmation",
            desc=f"**Order ID**: {order_id}\n\nAre you sure that you'd like to redeem the following reward?\n\n**Ticket Cost**: {reward["cost"]}\n**ID**: {reward["_id"]}\n"
            + f"**Name**: {reward["name"]}",
            view=confirm,
        )
        confirm.msg_ref = await interaction.original_response()
