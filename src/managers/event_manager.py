import helpers.pymongo_manager as pymongo_manager
import asyncio
from datetime import datetime, timedelta, timezone
from discord.ext import tasks
from helpers.time import *
from functions.message_scheduler.handlers import *
from helpers.message_scheduler.post import *
from helpers.message_scheduler.mongo_utils import *

bot = None


def init(b):
    global bot
    bot = b


@tasks.loop(seconds=5)
async def manageScheduleLoop():
    try:
        delay = getSecondsFromNextMinute()

        if delay == 0:
            return

        await asyncio.sleep(delay)

        # determining if there are any posts to be posted for the current minute
        date = datetime.now().astimezone(timezone.utc)

        epoch = datetime.utcfromtimestamp(0)

        posts = pymongo_manager.get_posts_in_date_range(
            epoch, date + timedelta(seconds=1)
        )

        # posting the posts if there are any
        for post in posts:
            try:
                await sendPost(post, bot)
                await deletePostById(post["_id"])
            except Exception as e:
                print(e)
    except Exception as e:
        print(e)


@manageScheduleLoop.before_loop
async def beforeLoop():
    await bot.wait_until_ready()
    print("Scheduling loop started")


async def handleReady():
    print("Bot connected")


async def handleMessageSchedule(ctx, bot, cmd, args):
    # creating a schedule and message object for new servers
    await registerServerWithDB(ctx)

    # interpreting commands
    try:
        if cmd == "add":
            await handleAdd(ctx, args)
        elif cmd == "remove":
            await handleRemove(ctx, args)
        elif cmd == "set":
            await handleSet(ctx, args)
        elif cmd == "reaction":
            await handleSetReaction(ctx, args)
        elif cmd == "reset":
            await handleReset(ctx)
        elif cmd == "clearSchedule":
            await handleClear(ctx)
        elif cmd == "preview":
            await handlePreview(ctx, bot, args)
        elif cmd == "list":
            await handleList(ctx)
        elif cmd == "help":
            await handleHelp(ctx)
        else:
            await sendEmbeddedMessage(
                ctx,
                0xFFFF00,
                {
                    "title": "Warning",
                    "desc": "Unrecognized command. Type '!ms help' for the list of commands!",
                },
            )
    except ValueError as e:  # this only throws if the user provided invalid arguments
        await sendEmbeddedMessage(ctx, 0xFF0000, {"title": "ERROR", "desc": e})
    except TypeError as e:
        await sendEmbeddedMessage(ctx, 0xFF0000, {"title": "ERROR", "desc": e})
    except RuntimeError as e:
        await sendEmbeddedMessage(ctx, 0xFF0000, {"title": "ERROR", "desc": e})
    except Exception as e:
        print(f"Error: {e}")
        await sendEmbeddedMessage(
            ctx,
            0xFF0000,
            {"title": "ERROR", "desc": "An error occurred. Command will be ignored."},
        )
