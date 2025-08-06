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
    @app_commands.describe()
    async def remove(
        self,
        interaction: discord.Interaction,
    ):
        await handle_command(
            self.handle_remove,
            interaction,
            self.__allowed_roles,
        )

    @app_commands.command(name="edit", description="Edits a reward")
    @app_commands.describe()
    async def edit(
        self,
        interaction: discord.Interaction,
    ):
        await handle_command(
            self.handle_edit,
            interaction,
            self.__allowed_roles,
        )

    ####################################################################################
    ################################### HANDLERS #######################################
    ####################################################################################
    async def handle_add(
        self,
        interaction: discord.Interaction,
        name: str,
        cost: int,
        pagecolour: str,
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

        # Wait for user to add a reward description
        msg = await wait_for_msg(
            interaction,
            self.bot,
            title="Enter a reward description",
            desc="Waiting for description...",
        )

        # store message
        images = []
        image = ""

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
            ObjectId(),
            {
                "name": name,
                "cost": cost,
                "page_colour": hex_clr,
                "desc": msg.content,
                "image": image,
            },
        )

        await send_success(
            interaction,
            "The reward has been added",
        )

    async def handle_remove(self, interaction: discord.Interaction) -> None:
        pass

    async def handle_edit(self, interaction: discord.Interaction) -> None:
        pass
