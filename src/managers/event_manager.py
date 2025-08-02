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
async def manage_schedule_loop():
    try:
        delay = get_seconds_from_next_minute()

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
                await send_post(post, bot)
                await delete_post_by_id(post["_id"])
            except Exception as e:
                print(e)
    except Exception as e:
        print(e)


@manage_schedule_loop.before_loop
async def before_loop():
    await bot.wait_until_ready()
    print("Scheduling loop started")


async def handle_ready():
    print("Bot connected")


async def handle_message_schedule(ctx, bot, cmd, args):
    # creating a schedule and message object for new servers
    await register_server_with_DB(ctx)

    # interpreting commands
    try:
        if cmd == "add":
            await handle_add(ctx, args)
        elif cmd == "remove":
            await handle_remove(ctx, args)
        elif cmd == "set":
            await handle_set(ctx, args)
        elif cmd == "reaction":
            await handle_set_reaction(ctx, args)
        elif cmd == "reset":
            await handle_reset(ctx)
        elif cmd == "clearSchedule":
            await handle_clear(ctx)
        elif cmd == "preview":
            await handle_preview(ctx, bot, args)
        elif cmd == "list":
            await handle_list(ctx)
        elif cmd == "help":
            await handle_help(ctx)
        else:
            await send_embedded_message(
                ctx,
                0xFFFF00,
                {
                    "title": "Warning",
                    "desc": "Unrecognized command. Type '!ms help' for the list of commands!",
                },
            )
    except ValueError as e:  # this only throws if the user provided invalid arguments
        await send_embedded_message(ctx, 0xFF0000, {"title": "ERROR", "desc": e})
    except TypeError as e:
        await send_embedded_message(ctx, 0xFF0000, {"title": "ERROR", "desc": e})
    except RuntimeError as e:
        await send_embedded_message(ctx, 0xFF0000, {"title": "ERROR", "desc": e})
    except Exception as e:
        print(f"Error: {e}")
        await send_embedded_message(
            ctx,
            0xFF0000,
            {"title": "ERROR", "desc": "An error occurred. Command will be ignored."},
        )
