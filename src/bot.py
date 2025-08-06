from commands.message_scheduler import MessageScheduler
from helpers.colours import Colour
from helpers.logger import *
import discord
from discord.ext import commands
from discord import app_commands
import os
from helpers.ticket_bot.mongo_utils import register_user_with_db
from helpers.validate import is_development
from managers.event_manager import *
import asyncio


# main bot driver function
def run_discord_bot():
    # initialization
    intents = discord.Intents.default()
    intents.message_content = True
    intents.typing = True
    intents.members = True

    bot = commands.Bot(command_prefix="!", intents=intents)
    event_manager = EventManager(bot)

    # trigger declarations
    @bot.tree.error
    async def on_bot_error(
        interaction: discord.Interaction, e: app_commands.AppCommandError
    ):
        Logger.exception(e)
        await send_error(interaction, "An error occurred.")

    @bot.event
    async def on_ready():
        try:
            Logger.info("Syncing commands...")

            if is_development():
                Logger.info("In development mode")

                await bot.tree.sync(
                    guild=discord.Object(id=int(os.environ["TEST_DISCORD_SERVER"]))
                )
            else:
                await bot.tree.sync()

            Logger.info("Bot ready")

            if not event_manager.manage_schedule_loop.is_running():
                event_manager.manage_schedule_loop.start()
        except Exception as e:
            Logger.exception(f"An error occurred on_ready: {e}")

    @bot.event
    async def on_member_join(member: discord.Member):
        if member.bot:
            return

        await register_user_with_db(member)

    async def start():
        async with bot:
            await bot.load_extension("commands.message_scheduler")
            await bot.load_extension("commands.ticket_bot.ticket_bot")
            await bot.load_extension("commands.ticket_bot.ticket_bot_admin")

            await bot.start(os.environ["TOKEN"])

    Logger.info("Starting bot")
    asyncio.run(start())
