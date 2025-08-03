import discord
from discord.ext.commands.bot import Bot
from helpers.logger import Logger


async def send_message(
    interaction: discord.Interaction,
    bot: Bot,
    content: str,
    channel: int | None = None,
    attachments: list | None = None,
) -> discord.Message:
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

        return await interaction.channel.send(content=res, files=attachments)
    except RuntimeError as e:
        raise e
    except ValueError as e:
        raise e
    except Exception as e:
        Logger.error(e)


async def send_message_by_channel_id(
    content: str, channel_id: int, bot: Bot, attachments: list | None = None
) -> discord.Message:
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
        Logger.error(e)


async def send_embedded_message(
    interaction: discord.Interaction,
    color: int | discord.Color | None,
    main_content: dict,
    fields: list | None = None,
    inline=False,
) -> None:
    embed_var = discord.Embed(
        title=main_content["title"], description=main_content["desc"], color=color
    )

    if fields:
        for field in fields:
            embed_var.add_field(name=field["name"], value=field["value"], inline=inline)

    await interaction.channel.send(embed=embed_var)
