from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from helpers.colours import Colour
from helpers.message_utils import (
    add_emojis,
    generate_embedded_message,
    send_error,
    send_message,
    send_success,
)


@pytest.mark.unit
class TestGenerateEmbeddedMessage:
    def test_builds_embed_with_fields_and_media(self):
        embed = generate_embedded_message(
            title="Hello",
            desc="Body",
            colour=Colour.GREEN,
            fields=[{"name": "A", "value": "1", "inline": True}],
            footer="footer",
            image="https://example.test/img.png",
            thumbnail="https://example.test/thumb.png",
        )
        assert embed.title == "Hello"
        assert embed.description == "Body"
        assert embed.color.value == Colour.GREEN
        assert embed.fields[0].name == "A"
        assert embed.fields[0].value == "1"
        assert embed.fields[0].inline is True
        assert embed.footer.text == "footer"
        assert embed.image.url == "https://example.test/img.png"
        assert embed.thumbnail.url == "https://example.test/thumb.png"


@pytest.mark.unit
class TestSendMessage:
    async def test_sends_to_channel_when_bot_and_channel_provided(self):
        channel = SimpleNamespace(send=AsyncMock(return_value="sent"))
        bot = SimpleNamespace(get_channel=lambda _id: channel)
        result = await send_message("hello", bot=bot, channel_id=10)
        channel.send.assert_awaited_once()
        assert result == "sent"

    async def test_raises_when_content_empty(self):
        with pytest.raises(ValueError, match="No message is set"):
            await send_message("")

    async def test_raises_when_channel_missing(self):
        bot = SimpleNamespace(get_channel=lambda _id: None)
        with pytest.raises(RuntimeError, match="Could not find channel"):
            await send_message("hello", bot=bot, channel_id=10)

    async def test_followup_when_interaction_provided(self):
        interaction = SimpleNamespace(
            followup=SimpleNamespace(send=AsyncMock(return_value="ok"))
        )
        result = await send_message("hello", interaction=interaction)
        interaction.followup.send.assert_awaited_once()
        assert result == "ok"


@pytest.mark.unit
class TestSendHelpers:
    async def test_send_error_uses_red_embed(self):
        interaction = SimpleNamespace(followup=SimpleNamespace(send=AsyncMock()))
        await send_error(interaction, "test")
        kwargs = interaction.followup.send.await_args.kwargs
        assert kwargs["embed"].title == "ERROR"
        assert kwargs["embed"].description == "test"
        assert kwargs["embed"].color.value == Colour.RED

    async def test_send_success_uses_green_embed(self):
        interaction = SimpleNamespace(followup=SimpleNamespace(send=AsyncMock()))
        await send_success(interaction, "done")
        kwargs = interaction.followup.send.await_args.kwargs
        assert kwargs["embed"].title == "Success"
        assert kwargs["embed"].description == "done"
        assert kwargs["embed"].color.value == Colour.GREEN

    async def test_add_emojis_falls_back_to_unicode(self):
        msg = SimpleNamespace(add_reaction=AsyncMock())
        await add_emojis(msg, custom_emojis=[], emojis=[":smile:"])
        msg.add_reaction.assert_awaited()
        msg.add_reaction.assert_awaited_with("😄")
