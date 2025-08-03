import discord
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
        Logger.error(e)

    # sending the message
    try:
        msg = await send_message_by_channel_id(
            post["message"], int(post["channel"]), bot, attachments
        )
    except RuntimeError as e:
        raise e
    except ValueError as e:
        raise e

    # adding emojis
    if server:
        for reaction in post["reactions"]:
            try:
                # set to a custom emoji by default
                emoji = discord.utils.get(server.emojis, name=reaction)

                if not emoji:  # standard emojis
                    emoji = reaction

                await msg.add_reaction(emoji)
            except:
                Logger.error(f"Unknown emoji: {reaction}")
