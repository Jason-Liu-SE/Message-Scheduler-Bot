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
    color: int | discord.Color | None,
    main_content: dict,
    fields: list | None = None,
    footer: str | None = None,
    image: str | None = None,
) -> None:
    embed_var = discord.Embed(
        title=main_content["title"],
        description=main_content["desc"],
        color=color,
    )

    if footer:
        embed_var.set_footer(footer)

    if image:
        embed_var.set_image(image)

    if fields:
        for field in fields:
            embed_var.add_field(
                name=field["name"],
                value=field["value"],
                inline=True if field["inline"] else False,
            )

    await interaction.followup.send(embed=embed_var)


async def wait_for_msg(
    interaction: discord.Interaction,
    bot: Bot,
    title: str = "Enter message",
    desc: str = "Waiting for message...",
) -> discord.Message:
    await send_embedded_message(
        interaction,
        Colour.LIGHT_BLUE,
        {"title": title, "desc": desc},
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


async def send_error(interaction: discord.Interaction, msg: str) -> None:
    await send_embedded_message(
        interaction, Colour.RED, {"title": "ERROR", "desc": msg}
    )


async def send_success(
    interaction: discord.Interaction,
    msg: str,
    title: str = "Success",
    colour: int | discord.Colour = Colour.GREEN,
):
    await send_embedded_message(
        interaction,
        colour,
        {
            "title": title,
            "desc": msg,
        },
    )
