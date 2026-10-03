from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import discord
from bson import ObjectId
from discord.ext import commands

from commands.message_scheduler.message_scheduler import MessageScheduler
from helpers.colours import Colour
from tests.fakes.discord import FakeChannel, FakeInteraction, FakeMember


def _scheduler():
    bot = commands.Bot(command_prefix="!", intents=discord.Intents.none())
    return MessageScheduler(bot)


@pytest.mark.integration
class TestMessageSchedulerHandlers:
    async def test_handle_add_schedules_message_and_resets_draft(
        self, fake_db, make_interaction
    ):
        guild_id = 100
        fake_db.seed(
            "messages",
            [
                {
                    "_id": guild_id,
                    "message": "Hello scheduled world",
                    "reactions": [":smile:"],
                    "attachments": {"message_id": "", "channel_id": ""},
                }
            ],
        )
        interaction = make_interaction(guild_id=guild_id)
        cog = _scheduler()

        await cog.handle_add(
            interaction,
            channel="555",
            day=12,
            month=12,
            year=2099,
            hour=15,
            minute=30,
        )

        schedules = fake_db["schedules"].docs
        assert len(schedules) == 1
        post = next(iter(schedules.values()))
        assert post["server_id"] == guild_id
        assert post["channel"] == 555
        assert post["message"] == "Hello scheduled world"
        assert fake_db["messages"].docs[guild_id]["message"] == ""
        success = interaction.followup.send.await_args.kwargs["embed"]
        assert "Post ID" in success.description

    async def test_handle_add_requires_set_message(self, fake_db, make_interaction):
        fake_db.seed(
            "messages",
            [
                {
                    "_id": 100,
                    "message": "",
                    "reactions": [],
                    "attachments": {"message_id": "", "channel_id": ""},
                }
            ],
        )
        cog = _scheduler()
        with pytest.raises(ValueError, match="No message was set"):
            await cog.handle_add(
                make_interaction(),
                channel="555",
                day=12,
                month=12,
                year=2099,
                hour=15,
                minute=30,
            )

    async def test_handle_remove_deletes_post(self, fake_db, make_interaction):
        post_id = ObjectId()
        fake_db.seed(
            "schedules",
            [{"_id": post_id, "server_id": 100, "message": "bye"}],
        )
        cog = _scheduler()
        await cog.handle_remove(make_interaction(), str(post_id))
        assert post_id not in fake_db["schedules"].docs

    async def test_handle_remove_rejects_unknown_post(self, fake_db, make_interaction):
        cog = _scheduler()
        with pytest.raises(ValueError, match="no scheduled post"):
            await cog.handle_remove(make_interaction(), str(ObjectId()))

    async def test_handle_list_empty_schedule_warns(self, fake_db, make_interaction):
        cog = _scheduler()
        interaction = make_interaction()
        await cog.handle_list(interaction)
        embed = interaction.followup.send.await_args.kwargs["embed"]
        assert embed.color.value == Colour.YELLOW
        assert "don't have any scheduled posts" in embed.description

    async def test_handle_list_shows_sorted_posts(self, fake_db, make_interaction):
        now = datetime.now()
        fake_db.seed(
            "schedules",
            [
                {
                    "_id": ObjectId(),
                    "server_id": 100,
                    "message": "second",
                    "time": now + timedelta(hours=2),
                },
                {
                    "_id": ObjectId(),
                    "server_id": 100,
                    "message": "first",
                    "time": now + timedelta(hours=1),
                },
            ],
        )
        interaction = make_interaction()
        await _scheduler().handle_list(interaction)
        embed = interaction.followup.send.await_args.kwargs["embed"]
        assert embed.title == "Posts"
        assert embed.description.index("first") < embed.description.index("second")

    async def test_handle_reset_and_clear(self, fake_db, make_interaction):
        fake_db.seed(
            "messages",
            [
                {
                    "_id": 100,
                    "message": "draft",
                    "reactions": [":x:"],
                    "attachments": {"message_id": "1", "channel_id": "2"},
                }
            ],
        )
        fake_db.seed(
            "schedules",
            [{"_id": ObjectId(), "server_id": 100, "message": "p"}],
        )
        cog = _scheduler()
        interaction = make_interaction()
        await cog.handle_reset(interaction)
        msg = fake_db["messages"].docs[100]
        assert msg["message"] == ""
        assert msg["reactions"] == []
        assert fake_db["schedules"].docs != {}

        await cog.handle_clear(interaction)
        assert fake_db["schedules"].docs == {}

    async def test_handle_preview_rejects_invalid_target(self, make_interaction):
        with pytest.raises(ValueError, match="current"):
            await _scheduler().handle_preview(make_interaction(), "bad")

    async def test_handle_help_includes_command_docs(self, make_interaction):
        interaction = make_interaction()
        await _scheduler().handle_help(interaction)
        embed = interaction.followup.send.await_args.kwargs["embed"]
        assert embed.title == "Message Scheduler Commands"
        assert any(field.name.endswith("add") for field in embed.fields)

    async def test_handle_set_reaction_extracts_emojis(self, fake_db, make_interaction):
        fake_db.seed(
            "messages",
            [
                {
                    "_id": 100,
                    "message": "hi",
                    "reactions": [],
                    "attachments": {"message_id": "", "channel_id": ""},
                }
            ],
        )
        interaction = make_interaction()
        await _scheduler().handle_set_reaction(interaction, ":smile: extra :wave:")
        assert fake_db["messages"].docs[100]["reactions"] == [":smile:", ":wave:"]
