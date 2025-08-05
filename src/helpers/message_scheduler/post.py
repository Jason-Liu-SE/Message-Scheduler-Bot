from discord.ext.commands.bot import Bot
from helpers.message_utils import *


async def send_post(post: dict, bot: Bot) -> None:
    server = await bot.fetch_guild(int(post["server_id"]))

    # adding attachments
    attachments = []

    try:
        if (
            post["attachments"]["message_id"] != ""
            and post["attachments"]["channel_id"] != ""
        ):
            channel = await bot.fetch_channel(int(post["attachments"]["channel_id"]))
            msg = await channel.fetch_message(int(post["attachments"]["message_id"]))

            for f in msg.attachments:
                file = await f.to_file()
                attachments.append(file)
    except Exception as e:
        Logger.error(f"Failed to add attachments to post message: {e}")

    # sending the message
    msg = await send_message_by_channel_id(
        post["message"], int(post["channel"]), bot, attachments, followup=False
    )

    # adding emojis
    try:
        if server:
            await add_emojis(msg, server.emojis, post["reactions"])
    except:
        Logger.error(f"Failed to add emojis to post message: {e}")
