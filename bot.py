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
  # intents.message_content = True    # needed for replit

  bot = commands.Bot(command_prefix='!', intents=intents)
  eventHandler.init(bot)

  # commands
  @bot.command(name='schedule')
  @commands.check(isAdmin)
  async def schedule(ctx, cmd, *args):
    await eventHandler.handleSchedule(ctx, bot, cmd, *args)


  @bot.command(name='scheduleHelp')
  @commands.check(isAdmin)
  async def scheduleHelp(ctx):
    await eventHandler.handleHelp(ctx)

  # trigger declaration
  @bot.event
  async def on_ready():
    await eventHandler.handleReady()

  # execution
  keep_alive()
  bot.run(os.environ['TOKEN'])
