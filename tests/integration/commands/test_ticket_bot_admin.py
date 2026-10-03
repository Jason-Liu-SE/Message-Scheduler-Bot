from unittest.mock import MagicMock

import pytest
import discord
from discord.ext import commands

from commands.ticket_bot.admin.ticket_bot_admin import TicketBotAdmin
from tests.fakes.discord import FakeGuild, FakeMember, FakeRole


def _bot():
    bot = commands.Bot(command_prefix="!", intents=discord.Intents.none())
    return TicketBotAdmin(bot)


@pytest.mark.integration
class TestTicketBotAdminHandlers:
    async def test_add_and_remove_and_set_tickets(
        self, fake_db, make_interaction, moderator_role
    ):
        user = FakeMember(5, "Dana")
        fake_db.seed("tickets", [{"_id": 5, "tickets": 10}])
        cog = _bot()
        interaction = make_interaction(roles=[moderator_role], extra_members=[user])

        await cog.handle_add(interaction, user, 4)
        assert fake_db["tickets"].docs[5]["tickets"] == 14

        await cog.handle_remove(interaction, user, 2)
        assert fake_db["tickets"].docs[5]["tickets"] == 12

        await cog.handle_set(interaction, user, 1)
        assert fake_db["tickets"].docs[5]["tickets"] == 1

    async def test_update_tickets_rejects_negative(self, make_interaction):
        cog = _bot()
        with pytest.raises(ValueError, match="non-negative"):
            await cog.update_tickets(make_interaction(), FakeMember(1), -1)

    async def test_creates_user_when_missing(self, fake_db, make_interaction):
        user = FakeMember(9, "New")
        interaction = make_interaction(extra_members=[user])
        await _bot().handle_set(interaction, user, 6)
        assert fake_db["tickets"].docs[9]["tickets"] == 6

    async def test_bulk_add_skips_ignore_role(self, fake_db, make_interaction):
        member_role = FakeRole(1, "Member")
        vip_role = FakeRole(2, "VIP")
        included = FakeMember(10, "In", roles=[member_role])
        excluded1 = FakeMember(11, "Out", roles=[member_role, vip_role])
        excluded2 = FakeMember(11, "Out", roles=[vip_role])
        guild = FakeGuild(members=[included, excluded1, excluded2])
        interaction = make_interaction(guild=guild)
        fake_db.seed(
            "tickets",
            [
                {"_id": 10, "tickets": 1, "incoming_trades": [], "outgoing_trades": []},
                {"_id": 11, "tickets": 1, "incoming_trades": [], "outgoing_trades": []},
                {"_id": 12, "tickets": 1, "incoming_trades": [], "outgoing_trades": []},
            ],
        )

        await _bot().handle_bulk_add(
            interaction, role=member_role, tickets=5, ignore_role=vip_role
        )

        assert fake_db["tickets"].docs[10]["tickets"] == 6
        assert fake_db["tickets"].docs[11]["tickets"] == 1
        assert fake_db["tickets"].docs[12]["tickets"] == 1

    async def test_help_lists_admin_commands(self, make_interaction):
        interaction = make_interaction()
        await _bot().handle_help(interaction)
        embed = interaction.followup.send.await_args.kwargs["embed"]
        assert embed.title == "Ticket Admin Commands"
