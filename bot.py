import discord
from discord.ext import commands
import os
import eventHandler


def isAdmin(ctx):
    return ctx.author.guild_permissions.administrator

# main bot driver function


def runDiscordBot():
    # initialization
    intents = discord.Intents.default()
    intents.typing = True
    intents.messages = True

    bot = commands.Bot(command_prefix='!', intents=intents)
    eventHandler.init(bot)

    # commands
    @bot.command(name='ms')
    @commands.check(isAdmin)
    async def messageScheduler(ctx, cmd='', *, args=''):
        await eventHandler.handleSchedule(ctx, bot, cmd, args)

    # trigger declaration
    @bot.event
    async def on_ready():
        await eventHandler.handleReady()

    # execution
    bot.run(os.environ['TOKEN'])
