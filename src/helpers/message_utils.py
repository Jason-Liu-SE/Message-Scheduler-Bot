import discord


async def sendMessage(message, bot, content, channel=None, attachments=None):
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


async def sendMessageByChannelID(content, channelID: int, bot, attachments=None):
    try:
        res = str(content)

        # content can't be empty
        if not content:
            raise ValueError("No message is set.")

        channel = bot.get_channel(channelID)

        # non-existent channel
        if not channel:
            raise RuntimeError(
                f"Could not find channel '{channelID}' to send the message to."
            )

        return await channel.send(content=res, files=attachments)
    except RuntimeError as e:
        raise e
    except ValueError as e:
        raise e
    except Exception as e:
        print(e)


async def sendEmbeddedMessage(message, col, mainContent, fields=None, inline=False):
    embedVar = discord.Embed(
        title=mainContent["title"], description=mainContent["desc"], color=col
    )

    if fields:
        for field in fields:
            embedVar.add_field(name=field["name"], value=field["value"], inline=inline)

    await message.channel.send(embed=embedVar)
