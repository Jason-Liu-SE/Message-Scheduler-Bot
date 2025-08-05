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
    ################################### COMMANDS #######################################
    ####################################################################################
    @app_commands.command(name="add", description="Adds tickets to a user")
    @app_commands.describe(
        user="User to add tickets to",
        tickets="The number of tickets to add",
    )
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
    @app_commands.describe(
        user="User to add tickets to", tickets="The number of tickets to add"
    )
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
    @app_commands.describe(
        user="User to add tickets to", tickets="The number of tickets to add"
    )
    async def set(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        tickets: app_commands.Range[int, 0],
    ):
        await handle_command(
            self.handle_set, interaction, self.__allowed_roles, user, tickets
        )

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
        multiplier: int = 1,
        is_override: bool = False,
    ) -> None:
        if tickets < 0:
            raise ValueError("Tickets must be non-negative")

        tickets *= multiplier

        try:
            user_obj = await get_user_object(user.id)

            if not user_obj:
                user_obj = {"tickets": 0, "incoming_trades": [], "outgoing_trades": []}

            user_obj["tickets"] = tickets + (0 if is_override else user_obj["tickets"])
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
                "desc": f"Updated user `{user.display_name}`'s tickets {"to" if is_override else "by"} {tickets}",
            },
        )

    async def handle_add(
        self, interaction: discord.Interaction, user: discord.Member, tickets: int
    ) -> None:
        await self.update_tickets(interaction, user, tickets)

    async def handle_remove(
        self, interaction: discord.Interaction, user: discord.Member, tickets: int
    ) -> None:
        await self.update_tickets(interaction, user, tickets, multiplier=-1)

    async def handle_set(
        self, interaction: discord.Interaction, user: discord.Member, tickets: int
    ) -> None:
        await self.update_tickets(interaction, user, tickets, is_override=True)

    async def handle_help(self, interaction: discord.Interaction) -> None:
        help_desc = """Ticket Admin is the administrative version of the Ticket bot. This bot allows those with sufficient permissions to add, remove, and set tickets for users.
        
    The commands are as follows:"""

        add_msg = """Adds tickets to a user. The value must be >= 0.
        
    Format: /ticketadmin add <user> <tickets>
        
    E.g. /ticketadmin add @user 2
    This would add 2 tickets to @user"""

        remove_msg = """Removes tickets from a user. This value must be >= 0.
        
    Format: /ticketadmin remove <user> <tickets>
        
    E.g. /ticketadmin remove @user 2
    This would remove 2 tickets from @user"""

        set_msg = """Sets a user's tickets. This value must be >= 0.
        
    Format: /ticketadmin set <user> <tickets>
        
    E.g. /ticketadmin set @user 2
    This would set @user's tickets to 2"""

        fields = [
            {"name": "add", "value": add_msg},
            {"name": "remove", "value": remove_msg},
            {"name": "set", "value": set_msg},
        ]

        await send_embedded_message(
            interaction,
            Colour.PURPLE,
            {"title": "Ticket Admin Commands", "desc": help_desc},
            fields,
        )


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
