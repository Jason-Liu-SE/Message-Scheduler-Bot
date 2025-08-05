import discord
from discord.ext import commands
from discord.ext.commands.bot import Bot
from discord import app_commands

from helpers.command_helper import *
from helpers.id_helpers import *
from helpers.message_utils import *
from helpers.ticket_bot.mongo_utils import *
from helpers.time import *
from helpers.validate import *


class TicketBotAdmin(
    commands.GroupCog, group_name="ticketadmin", group_description="Manage your tickets"
):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

        self.__allowed_roles = [
            807340774781878333,
            838169320461697085,
            "👁‍🗨 Head Moderator 👁‍🗨",
            "Administrator",
            "Admin",
        ]

    ####################################################################################
    ################################ AUTOCOMPLETE ######################################
    ####################################################################################

    ####################################################################################
    ################################### COMMANDS #######################################
    ####################################################################################
    @app_commands.command(name="add", description="Adds tickets to a user")
    @app_commands.describe(user="User to add tickets to")
    @app_commands.describe(tickets="The number of tickets to add")
    async def add(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        tickets: app_commands.Range[int, 0],
    ):
        await handle_command(
            self.handle_add, interaction, self.__allowed_roles, user, tickets
        )

    @app_commands.command(name="remove", description="Remove tickets from a user")
    async def remove(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        tickets: app_commands.Range[int, 0],
    ):
        await handle_command(
            self.handle_remove, interaction, self.__allowed_roles, user, tickets
        )

    @app_commands.command(name="set", description="Sets a user's tickets")
    async def set(self, interaction: discord.Interaction):
        await handle_command(self.handle_set, interaction, self.__allowed_roles)

    @app_commands.command(
        name="help", description="List more info about the Admin Ticket Bot commands"
    )
    async def help(self, interaction: discord.Interaction):
        await handle_command(self.handle_help, interaction, self.__allowed_roles)

    ####################################################################################
    ################################### HANDLERS #######################################
    ####################################################################################
    async def update_tickets(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        tickets: int,
        multiplier: int,
    ) -> None:
        if tickets < 0:
            raise ValueError("Tickets must be non-negative")

        tickets *= multiplier

        try:
            user_obj = await get_user_object(user.id)

            if not user_obj:
                raise Exception

            user_obj["tickets"] += tickets
            await update_user_object(user.id, user_obj)
        except Exception as e:
            await send_embedded_message(
                interaction,
                Colour.RED,
                {"title": "ERROR", "desc": "Could not update user's tickets"},
            )
            Logger.exception(e)
            return

        await send_embedded_message(
            interaction,
            Colour.GREEN,
            {
                "title": "Success",
                "desc": f"Updated user `{user.display_name}`'s tickets by {tickets}",
            },
        )

    async def handle_add(
        self, interaction: discord.Interaction, user: discord.Member, tickets: int
    ) -> None:
        await self.update_tickets(interaction, user, tickets, 1)

    async def handle_remove(
        self, interaction: discord.Interaction, user: discord.Member, tickets: int
    ) -> None:
        await self.update_tickets(interaction, user, tickets, -1)

    async def handle_set(self, interaction: discord.Interaction) -> None:
        pass

    async def handle_help(self, interaction: discord.Interaction) -> None:
        pass


# automatically ran when using load_extensions
async def setup(bot: Bot) -> None:
    # registers cog
    if is_development():
        await bot.add_cog(
            TicketBotAdmin(bot),
            guild=discord.Object(id=int(os.environ["TEST_DISCORD_SERVER"])),
        )
    else:
        await bot.add_cog(TicketBotAdmin(bot))
