from math import ceil
import discord
from discord import app_commands

from helpers.command_helper import *
from helpers.id_helpers import *
from helpers.message_utils import *
from helpers.ticket_bot.mongo_utils import *
from helpers.time import *
from helpers.validate import *


class TicketBotRewards(app_commands.Group):
    __ITEMS_PER_PAGE = 3

    def __init__(self, name: str, description: str, allowed_roles: list) -> None:
        super().__init__(name=name, description=description)
        self.__allowed_roles = allowed_roles
        self.bot = None  # set by the parent

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
                    {
                        "$expr": {
                            "$regexMatch": {
                                "input": {"$toString": "$_id"},
                                "regex": current,
                                "options": "i",
                            }
                        }
                    },
                ]
            },
            sort_field="name",
        )

        for reward_id, reward in rewards.items():
            if current.lower() in reward["name"] or current.lower() in f"{reward_id}":
                choices.append(
                    app_commands.Choice(
                        name=f"{reward_id} | {reward["name"][:30]}",
                        value=f"{reward_id}",
                    )
                )

        return choices

    # List
    ac_list_page = generate_autocomplete([], get_pages)

    # Inspect
    ac_inspect_item = generate_autocomplete([], get_reward_choices)

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
    async def redeem(self, interaction: discord.Interaction):
        await handle_command(self.handle_redeem, interaction, self.__allowed_roles)

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
        reward_ids = ""
        reward_names = ""
        reward_costs = ""

        for index, reward in enumerate(rewards.items()):
            reward_ids += f"`{reward[0]}`{"\n\n" if index + 1 < len(rewards) else ""}"
            reward_names += (
                f"{reward[1]["name"]}{"\n\n" if index + 1 < len(rewards) else ""}"
            )
            reward_costs += (
                f"{reward[1]["cost"]}{"\n\n" if index + 1 < len(rewards) else ""}"
            )

        await send_embedded_message(
            interaction,
            Colour.ORANGE,
            {"title": "Rewards  :shopping_bags:"},
            fields=[
                {"name": "ID", "value": reward_ids, "inline": True},
                {"name": "Name", "value": reward_names, "inline": True},
                {"name": "Ticket Cost", "value": reward_costs, "inline": True},
            ],
            footer=f"Page: {page}/{pages}  |  Items {skip + 1}-{skip + len(rewards)} of {num_rewards}",
        )

    async def handle_inspect(self, interaction: discord.Interaction, item: str) -> None:
        if not ObjectId.is_valid(item):
            raise ValueError(f"Item {item} is not valid")

        reward_id = ObjectId(item)

        try:
            reward = await get_reward_object(reward_id)
        except Exception as e:
            err_msg = f"Could not find any rewards with id: {reward_id}"
            Logger.error(f"{err_msg}: {e}")
            await send_error(interaction, err_msg)
            return

        try:
            page_colour = int(reward["page_colour"].split("x")[1], 16)
        except Exception as e:
            page_colour = None
            Logger.error(f"Page colour: '{reward["page_colour"]}' is invalid")

        await send_embedded_message(
            interaction,
            colour=page_colour,
            main_content={
                "title": f"Reward | {reward["name"]}",
                "desc": f"**ID**: {reward["_id"]}\n**Ticket Cost**: {reward["cost"]}{f"\n\n{reward["desc"]}" if len(reward["desc"]) > 0 else ""}",
            },
            image=reward["image"] if len(reward["image"]) > 0 else None,
        )

    async def handle_redeem(self, interaction: discord.Interaction) -> None:
        pass
