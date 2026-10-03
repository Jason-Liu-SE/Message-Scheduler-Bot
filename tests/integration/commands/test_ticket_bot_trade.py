from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import discord
from discord.ext import commands

from commands.ticket_bot.ticket_bot_trade import TicketBotTrade
from tests.fakes.discord import FakeMember


def _trade():
    group = TicketBotTrade(
        name="trade",
        description="trade",
        allowed_roles=["@everyone"],
    )
    group.bot = commands.Bot(command_prefix="!", intents=discord.Intents.none())
    return group


@pytest.mark.integration
class TestTicketBotTradeHandlers:
    async def test_cannot_trade_with_self(self, make_interaction):
        interaction = make_interaction()
        with pytest.raises(ValueError, match="yourself"):
            await _trade().handle_start(
                interaction,
                target_user=interaction.user,
                action="send",
                tickets=1,
            )

    async def test_requires_positive_tickets(self, fake_db, make_interaction):
        instigator = FakeMember(1, "A")
        target = FakeMember(2, "B")
        fake_db.seed(
            "tickets",
            [
                {"_id": 1, "tickets": 10},
                {"_id": 2, "tickets": 10},
            ],
        )
        interaction = make_interaction(user=instigator, extra_members=[target])
        with pytest.raises(ValueError, match="greater than 0"):
            await _trade().handle_start(interaction, target, "send", 0)

    async def test_start_send_posts_trade_embed(self, fake_db, make_interaction):
        instigator = FakeMember(1, "A")
        target = FakeMember(2, "B")
        third_party = FakeMember(3, "C")
        fake_db.seed(
            "tickets",
            [
                {"_id": 1, "tickets": 10},
                {"_id": 2, "tickets": 10},
                {"_id": 3, "tickets": 10},
            ],
        )
        interaction = make_interaction(user=instigator, extra_members=[target])
        await _trade().handle_start(interaction, target, "send", 3)
        embed = interaction.followup.send.await_args.kwargs["embed"]
        assert "Send" in embed.title
        assert "`3`" in embed.description
        view = interaction.followup.send.await_args.kwargs["view"]
        assert instigator.id in view.authorized_ids
        assert target.id in view.authorized_ids
        assert third_party.id not in view.authorized_ids
