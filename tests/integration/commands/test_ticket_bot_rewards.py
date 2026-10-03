from unittest.mock import MagicMock

import pytest
import discord
from bson import ObjectId
from discord.ext import commands

from commands.ticket_bot.ticket_bot_rewards import TicketBotRewards
from helpers.ticket_bot.format_helpers import display_stock


def _rewards():
    group = TicketBotRewards(
        name="rewards",
        description="rewards",
        allowed_roles=["@everyone"],
    )
    group.bot = commands.Bot(command_prefix="!", intents=discord.Intents.none())
    return group


def _reward(reward_id=None, name="Sticker", cost=5, stock=3, colour="0xFFAA00"):
    return {
        "_id": reward_id or ObjectId(),
        "name": name,
        "cost": cost,
        "stock": stock,
        "desc": "A fun sticker",
        "image": "",
        "page_colour": colour,
    }


@pytest.mark.integration
class TestTicketBotRewardsHandlers:
    async def test_list_paginates_and_shows_stock(self, fake_db, make_interaction):
        fake_db.seed(
            "rewards",
            [
                _reward(name="Alpha", stock=0),
                _reward(name="Beta", stock=-1),
            ],
        )
        interaction = make_interaction()
        await _rewards().handle_list(interaction, page=1)
        embed = interaction.followup.send.await_args.kwargs["embed"]
        assert embed.title.startswith("Rewards")
        values = " ".join(field.value for field in embed.fields)
        assert "OUT OF STOCK" in values
        assert "∞" in values
        assert "Page: 1/1" in embed.footer.text

    async def test_inspect_invalid_id(self, make_interaction):
        with pytest.raises(ValueError, match="not valid"):
            await _rewards().handle_inspect(make_interaction(), "bad")

    async def test_inspect_missing_reward(self, fake_db, make_interaction):
        interaction = make_interaction()
        await _rewards().handle_inspect(interaction, str(ObjectId()))
        embed = interaction.followup.send.await_args.kwargs["embed"]
        assert embed.title == "ERROR"

    async def test_inspect_renders_reward(self, fake_db, make_interaction):
        reward = _reward(name="Hat", cost=12, stock=4)
        fake_db.seed("rewards", [reward])
        interaction = make_interaction()
        await _rewards().handle_inspect(interaction, str(reward["_id"]))
        embed = interaction.followup.send.await_args.kwargs["embed"]
        assert "Hat" in embed.title
        assert "12" in embed.description
        assert str(display_stock(4)) in embed.description

    async def test_redeem_rejects_out_of_stock(self, fake_db, make_interaction):
        reward = _reward(stock=0)
        fake_db.seed("rewards", [reward])
        with pytest.raises(ValueError, match="OUT OF STOCK"):
            await _rewards().handle_redeem(make_interaction(), str(reward["_id"]))

    async def test_redeem_rejects_insufficient_tickets(self, fake_db, make_interaction):
        reward = _reward(cost=20, stock=2)
        user = make_interaction().user
        fake_db.seed("rewards", [reward])
        fake_db.seed("tickets", [{"_id": user.id, "tickets": 1}])
        with pytest.raises(ValueError, match="enough tickets"):
            await _rewards().handle_redeem(
                make_interaction(user=user), str(reward["_id"])
            )

    async def test_redeem_sends_confirmation(self, fake_db, make_interaction):
        reward = _reward(cost=5, stock=2)
        interaction = make_interaction()
        fake_db.seed("rewards", [reward])
        fake_db.seed("tickets", [{"_id": interaction.user.id, "tickets": 10}])
        await _rewards().handle_redeem(interaction, str(reward["_id"]))
        embed = interaction.followup.send.await_args.kwargs["embed"]
        assert embed.title == "Confirmation"
        assert str(reward["_id"]) in embed.description
