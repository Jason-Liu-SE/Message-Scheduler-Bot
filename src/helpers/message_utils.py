import discord


async def send_message(message, bot, content, channel=None, attachments=None):
    try:
        res = str(content)

        # content can't be empty
        if not content:
            raise ValueError("No message is set.")

        # specified channel
        if channel:
            c = bot.get_channel(channel)

            # non-existent channel
            if not c:
                raise RuntimeError(
                    f"Could not find channel '{channel}' to send the message to."
                )

            return await c.send(content=res, files=attachments)

        return await message.channel.send(content=res, files=attachments)
    except RuntimeError as e:
        raise e
    except ValueError as e:
        raise e
    except Exception as e:
        print(e)


async def send_message_by_channel_id(content, channel_id: int, bot, attachments=None):
    try:
        res = str(content)

        # content can't be empty
        if not content:
            raise ValueError("No message is set.")

        channel = bot.get_channel(channel_id)

        # non-existent channel
        if not channel:
            raise RuntimeError(
                f"Could not find channel '{channel_id}' to send the message to."
            )

        return await channel.send(content=res, files=attachments)
    except RuntimeError as e:
        raise e
    except ValueError as e:
        raise e
    except Exception as e:
        print(e)


async def send_embedded_message(message, col, main_content, fields=None, inline=False):
    embed_var = discord.Embed(
        title=main_content["title"], description=main_content["desc"], color=col
    )

    if fields:
        for field in fields:
            embed_var.add_field(name=field["name"], value=field["value"], inline=inline)

    await message.channel.send(embed=embed_var)
