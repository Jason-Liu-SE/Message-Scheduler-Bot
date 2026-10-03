from unittest.mock import MagicMock

import pytest
import discord
from bson import ObjectId
from discord.ext import commands

from commands.ticket_bot.ticket_bot import TicketBot
from helpers.colours import Colour
from tests.fakes.discord import FakeMember


def _ticket_bot():
    bot = commands.Bot(command_prefix="!", intents=discord.Intents.none())
    return TicketBot(bot)


@pytest.mark.integration
class TestTicketBotHandlers:
    async def test_balance_shows_tickets(
        self, fake_db, make_interaction, everyone_role
    ):
        user = FakeMember(11, "Alice", roles=[everyone_role])
        fake_db.seed("tickets", [{"_id": 11, "tickets": 42}])
        interaction = make_interaction(user=user)
        await _ticket_bot().handle_balance(interaction)
        embed = interaction.followup.send.await_args.kwargs["embed"]
        assert embed.title == "Alice's Tickets"
        assert embed.description == "42"

    async def test_balance_errors_when_user_missing(
        self, fake_db, make_interaction, everyone_role
    ):
        user = FakeMember(11, "Alice", roles=[everyone_role])
        interaction = make_interaction(user=user)
        await _ticket_bot().handle_balance(interaction)
        embed = interaction.followup.send.await_args.kwargs["embed"]
        assert embed.title == "ERROR"

    async def test_view_shows_target_tickets(
        self, fake_db, make_interaction, everyone_role
    ):
        target = FakeMember(22, "Bob")
        fake_db.seed("tickets", [{"_id": 22, "tickets": 7}])
        # testing one user checking the balance of another user
        interaction = make_interaction(roles=[everyone_role], extra_members=[target])
        await _ticket_bot().handle_view(interaction, target)
        embed = interaction.followup.send.await_args.kwargs["embed"]
        assert embed.title == "Bob's Tickets"
        assert embed.description == "7"

    async def test_leaderboard_empty(self, fake_db, make_interaction):
        interaction = make_interaction()
        await _ticket_bot().handle_leaderboard(interaction)
        embed = interaction.followup.send.await_args.kwargs["embed"]
        assert "No one has tickets yet" in embed.description

    async def test_leaderboard_ranks_members(self, fake_db, make_interaction):
        alice = FakeMember(1, "Alice")
        bob = FakeMember(2, "Bob")
        fake_db.seed(
            "tickets",
            [
                {"_id": 1, "tickets": 3},
                {"_id": 2, "tickets": 10},
            ],
        )
        interaction = make_interaction(user=alice, extra_members=[bob])
        await _ticket_bot().handle_leaderboard(interaction)
        embed = interaction.followup.send.await_args.kwargs["embed"]
        assert embed.fields[0].name.startswith("#1")
        assert "Bob" in embed.fields[0].name
        assert "10" in embed.fields[0].value

    async def test_help_lists_ticket_commands(self, make_interaction):
        interaction = make_interaction()
        await _ticket_bot().handle_help(interaction)
        embed = interaction.followup.send.await_args.kwargs["embed"]
        assert embed.title == "Ticket Commands"
        assert embed.color.value == Colour.PURPLE
