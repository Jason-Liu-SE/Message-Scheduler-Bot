import discord
from discord import app_commands

from helpers.command_helper import *
from helpers.id_helpers import *
from helpers.message_utils import *
from helpers.ticket_bot.mongo_utils import *
from helpers.time import *
from helpers.validate import *


class TicketBotAdminRewards(app_commands.Group):
    def __init__(self, name: str, description: str, allowed_roles: list) -> None:
        super().__init__(name=name, description=description)
        self.__allowed_roles = allowed_roles
        self.bot = None  # set by the parent

    ####################################################################################
    ################################ AUTOCOMPLETE ######################################
    ####################################################################################
    async def get_reward_choices(
        interaction: discord.Interaction, current: str
    ) -> list[app_commands.Choice]:
        choices = []

        current = current.strip()

        # rewards that partially match the current input in either id or name
        rewards = await get_many_reward_objects(
            {
                "$or": [
                    {"name": {"$regex": current, "$options": "i"}},
                    {"_id": {"$regex": current, "$options": "i"}},
                ]
            },
            sort_field="name",
        )

        for reward_id, reward in rewards.items():
            if current.lower() in reward["name"] or f"{reward_id}":
                choices.append(
                    app_commands.Choice(
                        name=f"{reward_id}: {reward["name"][:30]}", value=f"{reward_id}"
                    )
                )

        return choices

    # Remove
    ac_remove_item = generate_autocomplete([], get_reward_choices)

    # Edit
    ac_edit_item = generate_autocomplete([], get_reward_choices)

    ####################################################################################
    ################################### COMMANDS #######################################
    ####################################################################################
    @app_commands.command(name="add", description="Adds a reward")
    @app_commands.describe(
        name="Name of the reward",
        cost="Ticket cost of the reward",
        pagecolour="The hex colour of the reward's inspect page",
    )
    async def add(
        self,
        interaction: discord.Interaction,
        name: str,
        cost: app_commands.Range[int, 0],
        pagecolour: str = "FFFFFF",
    ):
        await handle_command(
            self.handle_add, interaction, self.__allowed_roles, name, cost, pagecolour
        )

    @app_commands.command(name="remove", description="Removes a reward")
    @app_commands.describe(item="ID of the item to be removed from listing")
    @app_commands.autocomplete(item=ac_remove_item)
    async def remove(
        self,
        interaction: discord.Interaction,
        item: str,
    ):
        await handle_command(
            self.handle_remove,
            interaction,
            self.__allowed_roles,
            item,
        )

    @app_commands.command(name="edit", description="Edits a reward")
    @app_commands.describe(
        item="ID of the item to edit",
        name="Name of the reward",
        cost="Ticket cost of the reward",
        pagecolour="The hex colour of the reward's inspect page",
        changedesc="True to change the description. False by default",
    )
    @app_commands.autocomplete(item=ac_edit_item)
    async def edit(
        self,
        interaction: discord.Interaction,
        item: str,
        name: str | None = None,
        cost: app_commands.Range[int, 0] | None = None,
        pagecolour: str | None = None,
        changedesc: bool = False,
    ):
        await handle_command(
            self.handle_edit,
            interaction,
            self.__allowed_roles,
            item,
            name,
            cost,
            pagecolour,
            changedesc,
        )

    ####################################################################################
    ################################### HANDLERS #######################################
    ####################################################################################
    async def handle_update_reward(
        self,
        interaction: discord.Interaction,
        id: ObjectId,
        name: str,
        cost: int,
        pagecolour: str,
        desc: str | None = None,
        img: str | None = None,  # Ensure img is valid, or don't pass it
    ) -> None:
        if cost < 0:
            raise ValueError("Cost must be non-negative")

        try:
            int_16 = int(pagecolour, 16)
            hex_clr = hex(int_16)
        except Exception as e:
            Logger.error(e)
            await send_error(
                interaction,
                "The provided pagecolour is not a valid hex value. Refer to /ticketadmin help",
            )
            return

        image = "" if not img else img
        content = desc

        # store message
        if not desc:
            # Wait for user to add a reward description
            msg = await wait_for_msg(
                interaction,
                self.bot,
                title="Enter a reward description",
                desc="Waiting for description...",
            )

            content = msg.content

            if not img:
                images = []

                if msg.attachments:
                    for attachment in msg.attachments:
                        if not attachment.content_type.startswith("image/"):
                            continue

                        images.append(attachment.url)

                        if len(images) >= 2:
                            await send_embedded_message(
                                interaction,
                                Colour.YELLOW,
                                {
                                    "title": "Warning",
                                    "desc": "Only the first attached image will be used",
                                },
                                image=image,
                            )
                            break

                        image = attachment.url

        await update_reward_object(
            id,
            {
                "name": name,
                "cost": cost,
                "page_colour": hex_clr,
                "desc": content,
                "image": image,
            },
        )

        await send_success(
            interaction,
            "The reward has been updated",
        )

    async def handle_add(
        self,
        interaction: discord.Interaction,
        name: str,
        cost: int,
        pagecolour: str,
    ) -> None:
        await self.handle_update_reward(
            interaction, id=ObjectId(), name=name, cost=cost, pagecolour=pagecolour
        )

    async def handle_remove(
        self, interaction: discord.Interaction, item_id: str
    ) -> None:
        if not ObjectId.is_valid(item_id):
            raise ValueError(f"Provided item id: `{item_id}` is incorrect")

        reward_id = ObjectId(item_id)
        reward = await get_reward_object(reward_id)

        if not reward:
            raise ValueError(f"No reward with id: `{item_id}` was found")

        await delete_reward_object(reward_id)

        await send_success(
            interaction,
            f"Item with id: `{item_id}`, name: `{reward["name"]}` was removed from the listing",
        )

    async def handle_edit(
        self,
        interaction: discord.Interaction,
        item_id: str,
        name: str | None,
        cost: app_commands.Range[int, 0] | None,
        pagecolour: str | None,
        changedesc: bool,
    ) -> None:
        if not ObjectId.is_valid(item_id):
            raise ValueError(f"Provided item id: `{item_id}` is incorrect")

        reward_id = ObjectId(item_id)
        reward = await get_reward_object(reward_id)

        if not reward:
            raise ValueError(f"No reward with id: `{item_id}` was found")

        await self.handle_update_reward(
            interaction,
            id=reward_id,
            name=name if name else reward["name"],
            cost=cost if cost else reward["cost"],
            pagecolour=pagecolour if pagecolour else reward["page_colour"],
            desc=None if changedesc else reward["desc"],
            img=None if changedesc else reward["image"],
        )
