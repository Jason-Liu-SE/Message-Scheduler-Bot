from unittest.mock import MagicMock, patch

import pytest
import discord
from discord.ext import commands

from commands.message_scheduler import message_scheduler as ms_mod
from commands.ticket_bot import ticket_bot as ticket_mod
from commands.ticket_bot.admin import ticket_bot_admin as admin_mod


@pytest.mark.integration
class TestCogSetup:
    async def test_setup_registers_cogs_outside_development(self, monkeypatch):
        monkeypatch.setenv("IS_DEV", "false")
        bot = commands.Bot(command_prefix="!", intents=discord.Intents.none())

        recorded = []

        async def capture(cog, **kwargs):
            recorded.append((type(cog).__name__, kwargs))

        bot.add_cog = capture
        await ms_mod.setup(bot)
        await ticket_mod.setup(bot)
        await admin_mod.setup(bot)

        names = [name for name, _ in recorded]
        assert names == ["MessageScheduler", "TicketBot", "TicketBotAdmin"]
        assert all(kwargs == {} for _, kwargs in recorded)
