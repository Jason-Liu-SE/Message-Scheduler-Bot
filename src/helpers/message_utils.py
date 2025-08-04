import discord
from discord.ext.commands.bot import Bot
from helpers.logger import Logger


async def send_message(
    content: str,
    bot: Bot | None = None,
    interaction: discord.Interaction | None = None,
    channel_id: int | None = None,
    attachments: list | None = None,
) -> discord.Message:
    try:
        res = str(content)

        # content can't be empty
        if not content:
            raise ValueError("No message is set.")

        # specified channel
        if channel_id and bot:
            c = bot.get_channel(channel_id)

            # non-existent channel
            if not c:
                raise RuntimeError(
                    f"Could not find channel '{channel_id}' to send the message to."
                )

            return await c.send(content=res, files=attachments)

        if not interaction:
            raise RuntimeError(
                "'interaction' must be provided when 'channel id' is not specified"
            )

        return await interaction.channel.send(content=res, files=attachments)
    except RuntimeError as e:
        raise e
    except ValueError as e:
        raise e
    except Exception as e:
        Logger.exception(e)


async def send_message_by_channel_id(
    content: str, channel_id: int, bot: Bot, attachments: list | None = None
) -> discord.Message:
    send_message_by_channel_id(
        content, channel_id=channel_id, bot=bot, attachments=attachments
    )


async def send_embedded_message(
    interaction: discord.Interaction,
    color: int | discord.Color | None,
    main_content: dict,
    fields: list | None = None,
    inline=False,
    defer=True,
) -> None:
    embed_var = discord.Embed(
        title=main_content["title"], description=main_content["desc"], color=color
    )

    if defer:
        await interaction.response.defer()

    if fields:
        for field in fields:
            embed_var.add_field(name=field["name"], value=field["value"], inline=inline)

    await interaction.followup.send(embed=embed_var)


async def wait_for_msg(interaction: discord.Interaction, bot: Bot) -> discord.Message:
    await send_embedded_message(
        interaction,
        0x037FFC,
        {"title": "Set", "desc": "Waiting for message..."},
    )

    def wait_for_input(msg: discord.Message):
        return (
            msg.author.id == interaction.user.id
            and msg.channel.id == interaction.channel.id
        )

    return await bot.wait_for("message", timeout=None, check=wait_for_input)
