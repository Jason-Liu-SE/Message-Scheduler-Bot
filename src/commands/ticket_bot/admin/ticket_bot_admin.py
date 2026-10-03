import discord
from discord.ext import commands
from discord.ext.commands.bot import Bot
from discord import app_commands

from commands.command_bot import CommandBot
from commands.ticket_bot.admin.ticket_bot_admin_rewards import TicketBotAdminRewards
from helpers.command_helper import *
from helpers.help_messages import TICKET_BOT_ADMIN_HELP_MSGS
from helpers.id_helpers import *
from helpers.message_utils import *
from helpers.ticket_bot.mongo_utils import *
from helpers.time import *
from helpers.validate import *


class TicketBotAdmin(
    commands.GroupCog,
    CommandBot,
    group_name="ticketadmin",
    group_description="Manage your tickets",
):
    _allowed_roles = [
        807340774781878333,
        838169320461697085,
        "👁‍🗨 Head Moderator 👁‍🗨",
        "Administrator",
        "Admin",
    ]

    def __init__(self, bot: Bot) -> None:
        self.__bot = bot
        self.rewards.bot = bot

    ####################################################################################
    ################################### GROUPS #########################################
    ####################################################################################
    rewards = TicketBotAdminRewards(
        name="rewards",
        description="Manage the rewards",
        allowed_roles=_allowed_roles,
    )

    ####################################################################################
    ################################### COMMANDS #######################################
    ####################################################################################
    @app_commands.command(name="add", description="Adds tickets to a user")
    @app_commands.describe(
        user="User to add tickets to",
        tickets="The number of tickets to add",
    )
    @enrich_command
    async def add(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        tickets: app_commands.Range[int, 0],
    ):
        await self.handle_add(interaction, user=user, tickets=tickets)

    @app_commands.command(name="remove", description="Remove tickets from a user")
    @app_commands.describe(
        user="User to add tickets to", tickets="The number of tickets to add"
    )
    @enrich_command
    async def remove(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        tickets: app_commands.Range[int, 0],
    ):
        await self.handle_remove(interaction, user=user, tickets=tickets)

    @app_commands.command(name="set", description="Sets a user's tickets")
    @app_commands.describe(
        user="User to add tickets to", tickets="The number of tickets to add"
    )
    @enrich_command
    async def set(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        tickets: app_commands.Range[int, 0],
    ):
        await self.handle_set(interaction, user=user, tickets=tickets)

    @app_commands.command(
        name="bulkadd", description="Adds tickets to all users with a specific role"
    )
    @app_commands.describe(
        role="Target user role",
        tickets="The number of tickets to add",
        ignore="The role of users to not add tickets to",
    )
    @enrich_command
    async def bulk_add(
        self,
        interaction: discord.Interaction,
        role: discord.Role,
        tickets: app_commands.Range[int, 0],
        ignore: discord.Role | None = None,
    ):
        await self.handle_bulk_add(
            interaction, role=role, tickets=tickets, ignore_role=ignore
        )

    @app_commands.command(
        name="bulkremove",
        description="Remove tickets from all users with a specific role",
    )
    @app_commands.describe(
        role="Target user role",
        tickets="The number of tickets to add",
        ignore="The role of users to not remove tickets from",
    )
    @enrich_command
    async def bulk_remove(
        self,
        interaction: discord.Interaction,
        role: discord.Role,
        tickets: app_commands.Range[int, 0],
        ignore: discord.Role | None = None,
    ):
        await self.handle_bulk_remove(interaction, role, tickets, ignore_role=ignore)

    @app_commands.command(
        name="bulkset", description="Sets the tickets of all users with a specific role"
    )
    @app_commands.describe(
        role="Target user role",
        tickets="The number of tickets to add",
        ignore="The role of users to not set tickets for",
    )
    @enrich_command
    async def bulk_set(
        self,
        interaction: discord.Interaction,
        role: discord.Role,
        tickets: app_commands.Range[int, 0],
        ignore: discord.Role | None = None,
    ):

        await self.handle_bulk_set(
            interaction, role=role, tickets=tickets, ignore_role=ignore
        )

    @app_commands.command(
        name="help", description="List more info about the Admin Ticket Bot commands"
    )
    @enrich_command
    async def help(self, interaction: discord.Interaction):
        await self.handle_help(interaction)

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
                user_obj = {"tickets": 0}

            user_obj["tickets"] = tickets + (0 if is_override else user_obj["tickets"])
            await update_user_object(user.id, user_obj)
        except Exception as e:
            Logger.exception(e)
            await send_error(interaction, "Could not update user's tickets")
            return

        await send_success(
            interaction,
            f"Updated user `{user.display_name}`'s tickets {"to" if is_override else "by"} {tickets}. "
            + f"Their new balance is: `{user_obj["tickets"]}` tickets",
        )

    async def bulk_update_tickets(
        self,
        interaction: discord.Interaction,
        role: discord.Role,
        tickets: int,
        multiplier: int = 1,
        is_override: bool = False,
        ignore_role: discord.Role | None = None,
    ) -> None:
        if tickets < 0:
            raise ValueError("Tickets must be non-negative")

        tickets *= multiplier

        if not interaction.guild:
            await send_error(interaction, "This command must be used in a server")
            return

        try:
            members = [
                m
                for m in interaction.guild.members
                if role in m.roles and (not ignore_role or ignore_role not in m.roles)
            ]
            member_ids = [m.id for m in members]

            await create_user_objects(member_ids)

            user_objs = await get_user_objects(member_ids)

            for user_id, user_obj in user_objs.items():
                user_objs[user_id]["tickets"] = tickets + (
                    0 if is_override else user_obj["tickets"]
                )

            await update_user_objects(user_objs)
        except Exception as e:
            await send_error(
                interaction,
                f"Could not update tickets for users with role: {role.name}",
            )
            Logger.exception(e)
            return

        await send_success(
            interaction,
            f"Updated tickets for users with role `{role.name}`"
            + f"{f" and not role `{ignore_role.name}`" if ignore_role else ""} {"to" if is_override else "by"} {tickets}",
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

    async def handle_bulk_add(
        self,
        interaction: discord.Interaction,
        role: discord.Member,
        tickets: int,
        ignore_role: discord.Role | None,
    ) -> None:
        await self.bulk_update_tickets(
            interaction, role, tickets, ignore_role=ignore_role
        )

    async def handle_bulk_remove(
        self,
        interaction: discord.Interaction,
        role: discord.Member,
        tickets: int,
        ignore_role: discord.Role | None,
    ) -> None:
        await self.bulk_update_tickets(
            interaction, role, tickets, multiplier=-1, ignore_role=ignore_role
        )

    async def handle_bulk_set(
        self,
        interaction: discord.Interaction,
        role: discord.Member,
        tickets: int,
        ignore_role: discord.Role | None,
    ) -> None:
        await self.bulk_update_tickets(
            interaction, role, tickets, is_override=True, ignore_role=ignore_role
        )

    async def handle_help(self, interaction: discord.Interaction) -> None:
        msgs = [
            {"name": f"[{i + 1}] {key}", "value": TICKET_BOT_ADMIN_HELP_MSGS[key]}
            for i, key in enumerate(
                key for key in TICKET_BOT_ADMIN_HELP_MSGS if key != "description"
            )
        ]

        await send_embedded_message(
            interaction,
            colour=Colour.PURPLE,
            title="Ticket Admin Commands",
            desc=TICKET_BOT_ADMIN_HELP_MSGS["description"],
            fields=msgs,
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
