import discord
from discord.ext import commands
import os
import helpers.eventHandler as eventHandler


def isAdmin(ctx):
    return ctx.author.guild_permissions.administrator


# main bot driver function


def runDiscordBot():
    # initialization
    intents = discord.Intents.default()
    intents.typing = True
    intents.messages = True

    bot = commands.Bot(command_prefix="!", intents=intents)
    eventHandler.init(bot)

    # commands
    @bot.command(name="ms")
    @commands.has_any_role(
        807340774781878333,
        838169320461697085,
        807340024088625192,
        "👁‍🗨 Head Moderator 👁‍🗨",
        "Moderator",
        "Administrator",
    )
    async def messageScheduler(ctx, cmd="", *, args=""):
        try:
            await eventHandler.handleSchedule(ctx, bot, cmd, args)
        except Exception as e:
            print(e)

    # trigger declaration
    @bot.event
    async def on_ready():
        try:
            await eventHandler.handleReady()
        except Exception as e:
            print(e)

    # execution
    eventHandler.manageScheduleLoop.start()
    bot.run(os.environ["TOKEN"])
