from enum import Enum
import discord
from discord.ext import commands
from discord import app_commands

from commands.message_scheduler.commands import *
from helpers.command_helper import handle_command


msAdmin = app_commands.Group(
    name="ms",
    description="Admin Message Scheduler commands",
)


class MessageScheduler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.__allowed_roles = [
            807340774781878333,
            838169320461697085,
            807340024088625192,
            "👁‍🗨 Head Moderator 👁‍🗨",
            "1145485853641146498",
            "Moderator",
            "Administrator",
        ]

    async def init(self):
        self.bot.tree.add_command(msAdmin)

    @msAdmin.command(name="add", description="Adds a set message to the schedule")
    async def add(self, interaction: discord.Interaction):
        handle_command(handle_add, interaction, self.__allowed_roles)

    @msAdmin.command(name="remove", description="Removes a message from the schedule")
    async def remove(self, interaction: discord.Interaction):
        handle_command(handle_remove, interaction, self.__allowed_roles)

    @msAdmin.command(
        name="set", description="Sets a message that'll be added to the schedule later"
    )
    async def set(self, interaction: discord.Interaction):
        handle_command(handle_set, interaction, self.__allowed_roles)

    @msAdmin.command(
        name="reaction", description="Adds reactions to the current message"
    )
    async def reaction(self, interaction: discord.Interaction):
        handle_command(handle_set_reaction, interaction, self.__allowed_roles)

    @msAdmin.command(name="reset", description="Clears the current message")
    async def reset(self, interaction: discord.Interaction):
        handle_command(handle_reset, interaction, self.__allowed_roles)

    @msAdmin.command(name="clearschedule", description="Removes all scheduled messages")
    async def clear_schedule(self, interaction: discord.Interaction):
        handle_command(handle_clear, interaction, self.__allowed_roles)

    @msAdmin.command(name="preview", description="Previews a specified message")
    async def preview(self, interaction: discord.Interaction):
        handle_command(handle_preview, interaction, self.__allowed_roles)

    @msAdmin.command(name="list", description="Lists all scheduled messages")
    async def list(self, interaction: discord.Interaction):
        handle_command(handle_list, interaction, self.__allowed_roles)

    @msAdmin.command(
        name="help", description="List more info about Message Scheduler commands"
    )
    async def help(self, interaction: discord.Interaction):
        handle_command(handle_help, interaction, self.__allowed_roles)
