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

    # Remove
    ac_list_page = generate_autocomplete([], get_pages)

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
    async def inspect(self, interaction: discord.Interaction):
        await handle_command(self.handle_inspect, interaction, self.__allowed_roles)

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

    async def handle_inspect(self, interaction: discord.Interaction) -> None:
        pass

    async def handle_redeem(self, interaction: discord.Interaction) -> None:
        pass
