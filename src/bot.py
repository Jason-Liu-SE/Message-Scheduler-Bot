import discord
from discord.ext import commands
import os
import managers.event_manager as event_manager


def isAdmin(ctx):
    return ctx.author.guild_permissions.administrator


# main bot driver function
def run_discord_bot():
    # initialization
    intents = discord.Intents.default()
    intents.message_content = True
    intents.typing = True

    bot = commands.Bot(command_prefix="!", intents=intents)
    event_manager.init(bot)

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
    async def message_scheduler(ctx, cmd="", *, args=""):
        try:
            await event_manager.handle_message_schedule(ctx, bot, cmd, args)
        except Exception as e:
            print(e)

    # trigger declaration
    @bot.event
    async def on_ready():
        try:
            await event_manager.handle_ready()

            if not event_manager.manage_schedule_loop.is_running():
                event_manager.manage_schedule_loop.start()
        except Exception as e:
            print(e)

    # execution
    bot.run(os.environ["TOKEN"])
