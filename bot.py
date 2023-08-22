import discord
from discord.ext import commands
import os
import eventHandler
from keep_alive import keep_alive


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
    @bot.command(name='poster')
    @commands.check(isAdmin)
    async def poster(ctx, cmd=None, *, args=None):
        await eventHandler.handlePoster(ctx, bot, cmd, args)

    @bot.command(name='posterHelp')
    @commands.check(isAdmin)
    async def posterHelp(ctx):
        await eventHandler.handleHelp(ctx)

    # trigger declaration
    @bot.event
    async def on_ready():
        await eventHandler.handleReady()

    # execution
    keep_alive()
    bot.run(os.environ['TOKEN'])
