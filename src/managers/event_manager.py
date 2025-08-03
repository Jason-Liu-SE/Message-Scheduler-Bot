import asyncio
from discord.ext import tasks
from helpers import pymongo_manager
from helpers.message_scheduler.mongo_utils import *
from helpers.message_scheduler.post import *
from helpers.time import *


class EventManager:
    def __init__(self, bot):
        self.bot = bot

    @tasks.loop(seconds=5)
    async def manage_schedule_loop(self):
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
                    await send_post(post, self.bot)
                    await delete_post_by_id(post["_id"])
                except Exception as e:
                    Logger.error(e)
        except Exception as e:
            Logger.error(e)

    @manage_schedule_loop.before_loop
    async def before_loop(self):
        await self.bot.wait_until_ready()
        Logger.info("Scheduling loop started")
