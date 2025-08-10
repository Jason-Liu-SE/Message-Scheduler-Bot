import discord
from discord.ext import commands
from discord.ext.commands.bot import Bot
from discord import app_commands

from commands.command_bot import CommandBot
from commands.ticket_bot.admin.ticket_bot_admin_rewards import TicketBotAdminRewards
from helpers.command_helper import *
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
        role="Target user role", tickets="The number of tickets to add"
    )
    @enrich_command
    async def bulk_add(
        self,
        interaction: discord.Interaction,
        role: discord.Role,
        tickets: app_commands.Range[int, 0],
    ):
        await self.handle_bulk_add(interaction, role=role, tickets=tickets)

    @app_commands.command(
        name="bulkremove",
        description="Remove tickets from all users with a specific role",
    )
    @app_commands.describe(
        role="Target user role", tickets="The number of tickets to add"
    )
    @enrich_command
    async def bulk_remove(
        self,
        interaction: discord.Interaction,
        role: discord.Role,
        tickets: app_commands.Range[int, 0],
    ):
        await self.handle_bulk_remove(interaction, role, tickets)

    @app_commands.command(
        name="bulkset", description="Sets the tickets of all users with a specific role"
    )
    @app_commands.describe(
        role="Target user role", tickets="The number of tickets to add"
    )
    @enrich_command
    async def bulk_set(
        self,
        interaction: discord.Interaction,
        role: discord.Role,
        tickets: app_commands.Range[int, 0],
    ):
        await self.handle_bulk_set(interaction, role=role, tickets=tickets)

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
            f"Updated user `{user.display_name}`'s tickets {"to" if is_override else "by"} {tickets}",
        )

    async def bulk_update_tickets(
        self,
        interaction: discord.Interaction,
        role: discord.Role,
        tickets: int,
        multiplier: int = 1,
        is_override: bool = False,
    ) -> None:
        if tickets < 0:
            raise ValueError("Tickets must be non-negative")

        tickets *= multiplier

        if not interaction.guild:
            await send_error(interaction, "This command must be used in a server")
            return

        try:
            members = [m for m in interaction.guild.members if role in m.roles]
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
            f"Updated tickets for users with role `{role.name}` {"to" if is_override else "by"} {tickets}",
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
        self, interaction: discord.Interaction, role: discord.Member, tickets: int
    ) -> None:
        await self.bulk_update_tickets(interaction, role, tickets)

    async def handle_bulk_remove(
        self, interaction: discord.Interaction, role: discord.Member, tickets: int
    ) -> None:
        await self.bulk_update_tickets(interaction, role, tickets, multiplier=-1)

    async def handle_bulk_set(
        self, interaction: discord.Interaction, role: discord.Member, tickets: int
    ) -> None:
        await self.bulk_update_tickets(interaction, role, tickets, is_override=True)

    async def handle_help(self, interaction: discord.Interaction) -> None:
        help_desc = (
            "Ticket Admin is the administrative version of the Ticket bot. This bot allows those with sufficient permissions to"
            + f"\n* add tickets\n* remove tickets\n* set tickets\n* add rewards\n* remove rewards\n* edit rewards\n\n### The commands are as follows:"
        )

        add_msg = (
            ">>> Adds tickets to a user.\n\n"
            + f"**Fields**:\n"
            + f"`user`: a user to add tickets to. Fill via autocomplete.\n"
            + f"`tickets`: the number of tickets to add to the user. Must be >= 0.\n"
            + f"\n**Format**: `/ticketadmin add <user> <tickets>`\n\n"
            + f"E.g. **/ticketadmin add @user 2**\nThis would add 2 tickets to @user"
        )

        remove_msg = (
            ">>> Removes tickets from a user.\n\n"
            + f"**Fields**:\n"
            + f"`user`: a user to remove tickets from. Fill via autocomplete.\n"
            + f"`tickets`: the number of tickets to remove from the user. Must be >= 0.\n"
            + f"\n**Format**: `/ticketadmin remove <user> <tickets>`\n\n"
            + f"E.g. **/ticketadmin remove @user 2**\nThis would remove 2 tickets from @user"
        )

        set_msg = (
            ">>> Sets a user's tickets.\n\n"
            + f"**Fields**:\n"
            + f"`user`: a user to set tickets for. Fill via autocomplete.\n"
            + f"`tickets`: the number of tickets to set the user at. Must be >= 0.\n"
            + f"\n**Format**: `/ticketadmin set <user> <tickets>`\n\n"
            + f"E.g. **/ticketadmin set @user 2**\nThis would set @user's tickets to 2"
        )

        bulkadd_msg = (
            ">>> Adds tickets to all user with a specific role.\n"
            + f"**Fields**:\n"
            + f"`role`: the role of users to add tickets to. Fill via autocomplete.\n"
            + f"`tickets`: the number of ticket to add to users with the role. Must be >= 0.\n"
            + f"\n**Format**: `/ticketadmin bulkadd <role> <tickets>`\n\n"
            + f"E.g. **/ticketadmin bulkadd @mods 2**\nThis would add 2 tickets to all @mods"
        )

        bulkremove_msg = (
            ">>> Removes tickets from all users with a specific role.\n\n"
            + f"**Fields**:\n"
            + f"`role`: the role of users to remove tickets from. Fill via autocomplete.\n"
            + f"`tickets`: the number of ticket to remove from users with the role. Must be >= 0.\n"
            + f"\n**Format**: `/ticketadmin bulkremove <role> <tickets>`\n\n"
            + f"E.g. **/ticketadmin bulkremove @mods 2**\nThis would remove 2 tickets from all @mods"
        )

        bulkset_msg = (
            ">>> Sets the ticket value for all users with a specific role.\n\n"
            + f"**Fields**:\n"
            + f"`role`: the role of users to set tickets for. Fill via autocomplete.\n"
            + f"`tickets`: the number of ticket to set users with the role at. Must be >= 0.\n"
            + f"\n**Format**: `/ticketadmin bulkset <role> <tickets>`\n\n"
            + f"E.g. **/ticketadmin bulkset @mods 2**\nThis would set all @mods' tickets to 2"
        )

        rewards_add_msg = (
            ">>> Adds a reward to the rewards listing.\n\n"
            + f"**Fields**:\n"
            + f"`name`: reward name.\n"
            + f"`cost`: reward cost. Must be >= 0.\n"
            + f"`stock` (optional): amount of the reward to sell. Negative values mean `unlimited`. Default=-1.\n"
            + f"`pagecolour` (optional): colour of the reward's `inspect` page. Must be a valid hex. Default=FFFFFF.\n\n"
            + f"After the initial `rewards add` command is sent, a followup message is required to set the description. "
            + f"You can attach an image to the reward when editing the description. One image can be attached. "
            + f"If more than one image is attached, the first attached image is taken.\n"
            + f"\n**Format**: `/ticketadmin rewards add <name> <cost> <*optional*:stock> <*optional*:pagecolour>`\n\n"
            + f"E.g. **/ticketadmin rewards add Diamonds 5 4 FFFF00**\n"
            + f"This would add a reward with name `Diamonds` for a cost of `5 tickets` with `4` items in stock. Additionally, "
            + f"the colour of the reward's `/ticketadmin rewards inspect` page would be yellow, or `FFFF00` in hex."
        )

        rewards_remove_msg = (
            ">>> Removes a reward from the listing, based on provided the reward id.\n\n"
            + f"**Fields**:\n"
            + f"`item`: ID of the item to be removed. This can be found on the `/ticket rewards list` listing.\n"
            + f"\n**Format**: `/ticketadmin rewards remove <item>`\n\n"
            + f"E.g. **/ticketadmin rewards remove 1231asd213**\nThis would attempt to remove a reward with id: `1231asd213`"
        )

        rewards_edit_msg = (
            ">>> This edits an existing reward.\n\n"
            + f"**Fields**:\n"
            + f"`item`: ID of the reward. Found via `/ticket rewards list`.\n"
            + f"`name` (optional): reward name.\n"
            + f"`cost` (optional): reward cost. Must be >= 0.\n"
            + f"`stock` (optional): amount of the reward to sell. Negative values mean `unlimited`.\n"
            + f"`pagecolour` (optional): colour of the reward's `inspect` page. Must be a valid hex.\n"
            + f"`changedesc` (optional): Set to True to be prompted to change the reward description.\n\n"
            + f"When an optional field is provided, the value will override the existing value on the reward. "
            + f"Non-specified values are left unchanged.\n"
            + f"\n**Format**: `/ticketadmin rewards edit <item> <*optional*:name> <*optional*:cost> <*optional*:stock> <*optional*:pagecolour> <*optional*:changedesc>`\n\n"
            + f"E.g. **/ticketadmin rewards edit 123asd123 `name:`z `changedesc:`True**\n"
            + f"Reward `123asd123` would have its name updated to `z`. Its cost, stock, and pagecolour "
            + f"would not be changed. Since `changedesc` = True, a description prompt would appear, which could be used to change the reward image."
        )

        fields = [
            {"name": "[1] add", "value": add_msg},
            {"name": "[2] remove", "value": remove_msg},
            {"name": "[3] set", "value": set_msg},
            {"name": "[4] bulkadd", "value": bulkadd_msg},
            {"name": "[5] bulkremove", "value": bulkremove_msg},
            {"name": "[6] bulkset", "value": bulkset_msg},
            {"name": "[7] rewards add", "value": rewards_add_msg},
            {"name": "[8] rewards remove", "value": rewards_remove_msg},
            {"name": "[9] rewards edit", "value": rewards_edit_msg},
        ]

        await send_embedded_message(
            interaction,
            colour=Colour.PURPLE,
            title="Ticket Admin Commands",
            desc=help_desc,
            fields=fields,
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
