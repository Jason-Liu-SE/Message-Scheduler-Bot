from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from bson import ObjectId

from helpers.message_scheduler.post import send_post
from managers.event_manager import EventManager


@pytest.mark.integration
class TestSendPost:
    async def test_sends_message_and_reactions(self):
        sent_message = SimpleNamespace(add_reaction=AsyncMock())
        dest = SimpleNamespace(
            send=AsyncMock(return_value=sent_message)
        )
        bot = SimpleNamespace(
            fetch_guild=AsyncMock(return_value=SimpleNamespace(emojis=[])),
            fetch_channel=AsyncMock(),
            get_channel=lambda _id: dest,
        )
        post = {
            "server_id": 1,
            "channel": 2,
            "message": "hello",
            "reactions": [":smile:"],
            "attachments": {"message_id": "", "channel_id": ""},
        }
        with patch(
            "helpers.message_scheduler.post.send_message_by_channel_id",
            new=AsyncMock(return_value=sent_message),
        ) as send_message:
            await send_post(post, bot)

        send_message.assert_awaited_once_with(
            "hello",
            2,
            bot,
            [],
            followup=False,
        )
        sent_message.add_reaction.assert_awaited_once()
        bot.fetch_guild.assert_awaited_once_with(1)

    async def test_copies_attachments_when_present(self):
        attachment = SimpleNamespace(to_file=AsyncMock(return_value="file"))
        source_msg = SimpleNamespace(attachments=[attachment])
        channel = SimpleNamespace(fetch_message=AsyncMock(return_value=source_msg))
        dest = SimpleNamespace(send=AsyncMock(return_value=SimpleNamespace(add_reaction=AsyncMock())))
        bot = SimpleNamespace(
            fetch_guild=AsyncMock(return_value=SimpleNamespace(emojis=[])),
            fetch_channel=AsyncMock(return_value=channel),
            get_channel=lambda _id: dest,
        )
        post = {
            "server_id": 1,
            "channel": 9,
            "message": "with file",
            "reactions": [],
            "attachments": {"message_id": "11", "channel_id": "22"},
        }
        await send_post(post, bot)
        dest.send.assert_awaited_once()
        assert dest.send.await_args.kwargs["files"] == ["file"]

    async def test_attachment_failure_still_sends_message(self):
        dest = SimpleNamespace(send=AsyncMock(return_value=SimpleNamespace()))
        bot = SimpleNamespace(
            fetch_guild=AsyncMock(return_value=None),
            fetch_channel=AsyncMock(side_effect=RuntimeError("source unavailable")),
            get_channel=lambda _id: dest,
        )
        post = {
            "server_id": 1,
            "channel": 9,
            "message": "text survives",
            "reactions": [],
            "attachments": {"message_id": "11", "channel_id": "22"},
        }

        await send_post(post, bot)

        dest.send.assert_awaited_once_with(content="text survives", files=[])

    async def test_emoji_failure_is_logged_after_message_is_sent(self, quiet_logger):
        message = SimpleNamespace(add_reaction=AsyncMock(side_effect=RuntimeError("bad emoji")))
        dest = SimpleNamespace(send=AsyncMock(return_value=message))
        bot = SimpleNamespace(
            fetch_guild=AsyncMock(return_value=SimpleNamespace(emojis=[])),
            fetch_channel=AsyncMock(),
            get_channel=lambda _id: dest,
        )
        post = {
            "server_id": 1,
            "channel": 9,
            "message": "text",
            "reactions": [":bad:"],
            "attachments": {"message_id": "", "channel_id": ""},
        }

        await send_post(post, bot)

        dest.send.assert_awaited_once()
        quiet_logger.error.assert_called_once()


@pytest.mark.integration
class TestEventManager:
    async def test_loop_sends_due_posts_and_deletes_them(self):
        post = {"_id": ObjectId(), "message": "due"}
        bot = MagicMock()
        manager = EventManager(bot)

        with (
            patch("managers.event_manager.get_seconds_from_next_minute", return_value=1),
            patch("managers.event_manager.asyncio.sleep", new_callable=AsyncMock),
            patch(
                "managers.event_manager.get_posts_in_date_range",
                return_value=[post],
            ),
            patch(
                "managers.event_manager.send_post", new_callable=AsyncMock
            ) as send,
            patch(
                "managers.event_manager.delete_post_by_id", new_callable=AsyncMock
            ) as delete,
        ):
            await EventManager.manage_schedule_loop.coro(manager)

        send.assert_awaited_once_with(post, bot)
        delete.assert_awaited_once_with(post["_id"])

    async def test_loop_skips_when_delay_is_zero(self):
        manager = EventManager(MagicMock())
        with (
            patch("managers.event_manager.get_seconds_from_next_minute", return_value=0),
            patch(
                "managers.event_manager.send_post", new_callable=AsyncMock
            ) as send,
        ):
            await EventManager.manage_schedule_loop.coro(manager)
        send.assert_not_awaited()

    async def test_before_loop_waits_for_bot_ready(self):
            bot = MagicMock()
            bot.wait_until_ready = AsyncMock()
            manager = EventManager(bot)

            await manager.before_loop()

            bot.wait_until_ready.assert_awaited_once()
