from enum import Enum
import discord
from discord.ext import commands
from discord import app_commands


msAdmin = app_commands.Group(
    name="ms admin",
    description="Admin Message Scheduler commands",
    guild_ids=[1142203767513690193],
)


class MSCommands(Enum):
    ADD = ("add",)
    REMOVE = ("remove",)
    SET = ("set",)
    REACTION = ("reaction",)
    RESET = ("reset",)
    CLEARSCHEDULE = ("clearschedule",)
    PREVIEW = ("preview",)
    LIST = ("list",)
    HELP = ("help",)


class MessageScheduler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def init(self):
        self.bot.tree.add_command(msAdmin)

    async def handle_command(self, interaction: discord.Interaction):
        # # creating a schedule and message object for new servers
        # await register_server_with_DB(ctx)
        # await interaction.response.send_message("Add")
        # # interpreting commands
        # try:
        #     if cmd == "add":
        #         await handle_add(ctx, args)
        #     elif cmd == "remove":
        #         await handle_remove(ctx, args)
        #     elif cmd == "set":
        #         await handle_set(ctx, args)
        #     elif cmd == "reaction":
        #         await handle_set_reaction(ctx, args)
        #     elif cmd == "reset":
        #         await handle_reset(ctx)
        #     elif cmd == "clearSchedule":
        #         await handle_clear(ctx)
        #     elif cmd == "preview":
        #         await handle_preview(ctx, bot, args)
        #     elif cmd == "list":
        #         await handle_list(ctx)
        #     elif cmd == "help":
        #         await handle_help(ctx)
        #     else:
        #         await send_embedded_message(
        #             ctx,
        #             0xFFFF00,
        #             {
        #                 "title": "Warning",
        #                 "desc": "Unrecognized command. Type '!ms help' for the list of commands!",
        #             },
        #         )
        # except (
        #     ValueError
        # ) as e:  # this only throws if the user provided invalid arguments
        #     await send_embedded_message(ctx, 0xFF0000, {"title": "ERROR", "desc": e})
        # except TypeError as e:
        #     await send_embedded_message(ctx, 0xFF0000, {"title": "ERROR", "desc": e})
        # except RuntimeError as e:
        #     await send_embedded_message(ctx, 0xFF0000, {"title": "ERROR", "desc": e})
        # except Exception as e:
        #     Logger.error(e)
        #     await send_embedded_message(
        #         ctx,
        #         0xFF0000,
        #         {
        #             "title": "ERROR",
        #             "desc": "An error occurred. Command will be ignored.",
        #         },
        #     )
        pass

    @msAdmin.command(name="add", description="Adds a set message to the schedule")
    async def add(self, interaction: discord.Interaction):
        self.handle_command(interaction)

    @msAdmin.command(name="remove", description="Removes a message from the schedule")
    async def remove(self, interaction: discord.Interaction):
        self.handle_command(interaction)

    @msAdmin.command(
        name="set", description="Sets a message that'll be added to the schedule later"
    )
    async def set(self, interaction: discord.Interaction):
        self.handle_command(interaction)

    @msAdmin.command(
        name="reaction", description="Adds reactions to the current message"
    )
    async def reaction(self, interaction: discord.Interaction):
        self.handle_command(interaction)

    @msAdmin.command(name="reset", description="Clears the current message")
    async def reset(self, interaction: discord.Interaction):
        self.handle_command(interaction)

    @msAdmin.command(name="clearschedule", description="Removes all scheduled messages")
    async def clear_schedule(self, interaction: discord.Interaction):
        self.handle_command(interaction)

    @msAdmin.command(name="preview", description="Previews a specified message")
    async def preview(self, interaction: discord.Interaction):
        self.handle_command(interaction)

    @msAdmin.command(name="list", description="Lists all scheduled messages")
    async def list(self, interaction: discord.Interaction):
        self.handle_command(interaction)

    @msAdmin.command(
        name="help", description="List more info about Message Scheduler commands"
    )
    @app_commands.checks.has_any_role(
        [
            # 807340774781878333,
            # 838169320461697085,
            # 807340024088625192,
            # "👁‍🗨 Head Moderator 👁‍🗨",
            "1145485853641146498",
            "Moderator",
            # "Administrator",
        ]
    )
    async def help(self, interaction: discord.Interaction):
        self.handle_command(interaction)
