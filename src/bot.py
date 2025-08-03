from helpers.logger import *
import discord
from discord.ext import commands
import os
from managers.event_manager import *
from commands.message_scheduler.message_scheduler import *


# main bot driver function
def run_discord_bot():
    # initialization
    intents = discord.Intents.default()
    intents.message_content = True
    intents.typing = True

    bot = commands.Bot(command_prefix="!", intents=intents)
    event_manager = EventManager(bot)

    # trigger declaration
    @bot.event
    async def on_ready():
        try:
            Logger.info("Adding commands...")

            ms = MessageScheduler(bot)
            await bot.add_cog(ms)
            await ms.init()

            is_dev = os.getenv("IS_DEV")

            if is_dev != None and is_dev.lower() == "true":
                Logger.info("In development mode")

                await bot.tree.sync(
                    guild=discord.Object(id=int(os.environ["TEST_DISCORD_SERVER"]))
                )
            else:
                await bot.tree.sync()

            Logger.info("Bot connected")

            if not event_manager.manage_schedule_loop.is_running():
                event_manager.manage_schedule_loop.start()
        except Exception as e:
            Logger.error(e)

    # execution
    bot.run(os.environ["TOKEN"])
