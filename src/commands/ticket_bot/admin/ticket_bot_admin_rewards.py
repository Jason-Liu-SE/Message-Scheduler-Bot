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

    ####################################################################################
    ################################ AUTOCOMPLETE ######################################
    ####################################################################################

    ####################################################################################
    ################################### COMMANDS #######################################
    ####################################################################################
    @app_commands.command(name="add", description="Adds a reward")
    @app_commands.describe()
    async def rewards_add(
        self,
        interaction: discord.Interaction,
    ):
        await handle_command(
            self.handle_rewards_add,
            interaction,
            self.__allowed_roles,
        )

    @app_commands.command(name="remove", description="Removes a reward")
    @app_commands.describe()
    async def rewards_remove(
        self,
        interaction: discord.Interaction,
    ):
        await handle_command(
            self.handle_rewards_remove,
            interaction,
            self.__allowed_roles,
        )

    @app_commands.command(name="edit", description="Edits a reward")
    @app_commands.describe()
    async def rewards_edit(
        self,
        interaction: discord.Interaction,
    ):
        await handle_command(
            self.handle_rewards_edit,
            interaction,
            self.__allowed_roles,
        )

    ####################################################################################
    ################################### HANDLERS #######################################
    ####################################################################################
    async def handle_rewards_add(self, interaction: discord.Interaction) -> None:
        pass

    async def handle_rewards_remove(self, interaction: discord.Interaction) -> None:
        pass

    async def handle_rewards_edit(self, interaction: discord.Interaction) -> None:
        pass
