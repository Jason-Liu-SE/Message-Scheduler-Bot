from dataclasses import MISSING
import discord
from discord.ext.commands.bot import Bot
from emoji import emojize
from helpers.colours import Colour
from helpers.logger import Logger


async def send_message(
    content: str,
    bot: Bot | None = None,
    interaction: discord.Interaction | None = None,
    channel_id: int | None = None,
    attachments: list = [],
    followup: bool = True,
) -> discord.Message:
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
            "'interaction' must be provided when 'channel id' or 'bot' is not specified"
        )

    if followup:
        return await interaction.followup.send(content=res, files=attachments)
    else:
        return await interaction.response.send_message(content=res, files=attachments)


async def send_message_by_channel_id(
    content: str,
    channel_id: int,
    bot: Bot,
    attachments: list = [],
    followup: bool = True,
) -> discord.Message:
    return await send_message(
        content,
        channel_id=channel_id,
        bot=bot,
        attachments=attachments,
        followup=followup,
    )


async def send_embedded_message(
    interaction: discord.Interaction,
    title: str = None,
    desc: str = None,
    colour: int | discord.Color | None = None,
    fields: list | None = None,
    footer: str | None = None,
    image: str | None = None,
    thumbnail: str | None = None,
    view: discord.ui.View | None = None,
    ephemeral: bool = False,
) -> None:
    embed = generate_embedded_message(
        title=title,
        desc=desc,
        colour=colour,
        fields=fields,
        footer=footer,
        image=image,
        thumbnail=thumbnail,
    )

    await interaction.followup.send(
        embed=embed, view=view if view else discord.utils.MISSING, ephemeral=ephemeral
    )


async def send_existing_embedded_message(
    interaction: discord.Interaction,
    embed: discord.Embed,
    view: discord.ui.View = None,
    ephemeral: bool = False,
) -> None:
    await interaction.followup.send(
        embed=embed, view=view if view else discord.utils.MISSING, ephemeral=ephemeral
    )


def generate_embedded_message(
    title: str | None = None,
    desc: str | None = None,
    colour: int | discord.Color | None = None,
    fields: list | None = None,
    footer: str | None = None,
    image: str | None = None,
    thumbnail: str | None = None,
):
    embed = discord.Embed(
        title=title,
        description=desc,
        color=colour,
    )

    if footer:
        embed.set_footer(text=footer)

    if image:
        embed.set_image(url=image)

    if thumbnail:
        embed.set_thumbnail(url=thumbnail)

    if fields:
        for field in fields:
            embed.add_field(
                name=None if not "name" in field else field["name"],
                value=None if not "value" in field else field["value"],
                inline=False if not "inline" in field else field["inline"],
            )

    return embed


async def wait_for_msg(
    interaction: discord.Interaction,
    bot: Bot,
    title: str = "Enter message",
    desc: str = "Waiting for message...",
) -> discord.Message:
    await send_embedded_message(
        interaction,
        colour=Colour.LIGHT_BLUE,
        title=title,
        desc=desc,
    )

    def wait_for_input(msg: discord.Message):
        return (
            msg.author.id == interaction.user.id
            and msg.channel.id == interaction.channel.id
        )

    return await bot.wait_for("message", timeout=None, check=wait_for_input)


async def add_emojis(msg: discord.Message, custom_emojis: list, emojis: list) -> None:
    # adding emojis
    for reaction in emojis:
        try:
            # set to a custom emoji by default
            emoji = discord.utils.get(custom_emojis, name=reaction.strip(":"))

            if not emoji:  # standard emojis
                emoji = emojize(reaction, language="alias")

            await msg.add_reaction(emoji)
        except Exception as e:
            Logger.error(f"Unknown emoji: {reaction}")


async def send_error(
    interaction: discord.Interaction, msg: str, ephemeral: bool = False
) -> None:
    await send_embedded_message(
        interaction, colour=Colour.RED, title="ERROR", desc=msg, ephemeral=ephemeral
    )


async def send_success(
    interaction: discord.Interaction,
    msg: str,
    title: str = "Success",
    colour: int | discord.Colour = Colour.GREEN,
):
    await send_embedded_message(
        interaction,
        title=title,
        desc=msg,
        colour=colour,
    )
