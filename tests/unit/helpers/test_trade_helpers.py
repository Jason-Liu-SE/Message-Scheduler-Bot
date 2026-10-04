from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from helpers.ticket_bot.trade_helpers import (
    complete_trade,
    display_confirmation,
    update_confirmation_state,
    update_trade_msg,
    verify_trade_users,
)
from tests.fakes.discord import FakeMember


@pytest.mark.unit
class TestConfirmationHelpers:
    def test_update_confirmation_state_sets_matching_user(self):
        states = {1: False, 2: False}
        update_confirmation_state(2, states, True)
        assert states == {1: False, 2: True}

    def test_display_confirmation(self):
        assert display_confirmation(True) == ":white_check_mark:"
        assert display_confirmation(False) == ":x:"


@pytest.mark.unit
class TestCompleteTrade:
    async def test_moves_tickets_instigator_to_target(self):
        instigator = FakeMember(1, "A")
        target = FakeMember(2, "B")
        users = {1: {"tickets": 10}, 2: {"tickets": 1}}

        with patch(
            "helpers.ticket_bot.trade_helpers.update_user_objects",
            new_callable=AsyncMock,
        ) as update:
            await complete_trade(instigator, target, users, tickets=4)

        assert users[1]["tickets"] == 6
        assert users[2]["tickets"] == 5
        update.assert_awaited_once_with(users)

    async def test_moves_tickets_target_to_instigator(self):
        instigator = FakeMember(1, "A")
        target = FakeMember(2, "B")
        users = {1: {"tickets": 2}, 2: {"tickets": 8}}

        with patch(
            "helpers.ticket_bot.trade_helpers.update_user_objects",
            new_callable=AsyncMock,
        ):
            await complete_trade(
                instigator,
                target,
                users,
                tickets=3,
                send_direction="target_to_instigator",
            )

        assert users[1]["tickets"] == 5
        assert users[2]["tickets"] == 5


@pytest.mark.unit
class TestVerifyTradeUsers:
    async def test_raises_when_user_missing(self):
        instigator = FakeMember(1, "A")
        target = FakeMember(2, "B")
        with patch(
            "helpers.ticket_bot.trade_helpers.get_user_objects",
            new_callable=AsyncMock,
            return_value={1: {"tickets": 10}},
        ):
            with pytest.raises(ValueError, match="does not exist"):
                await verify_trade_users(instigator, target, tickets=1)

    async def test_raises_when_balance_too_low(self):
        instigator = FakeMember(1, "A")
        target = FakeMember(2, "B")
        with patch(
            "helpers.ticket_bot.trade_helpers.get_user_objects",
            new_callable=AsyncMock,
            return_value={1: {"tickets": 1}, 2: {"tickets": 10}},
        ):
            with pytest.raises(ValueError, match="does not have enough tickets"):
                await verify_trade_users(instigator, target, tickets=5)

    async def test_returns_users_when_valid(self):
        instigator = FakeMember(1, "A")
        target = FakeMember(2, "B")
        users = {1: {"tickets": 10}, 2: {"tickets": 10}}
        with patch(
            "helpers.ticket_bot.trade_helpers.get_user_objects",
            new_callable=AsyncMock,
            return_value=users,
        ):
            result = await verify_trade_users(instigator, target, tickets=5)
        assert result is users


@pytest.mark.unit
class TestUpdateTradeMsg:
    async def test_requires_message_ref(self):
        view = type("V", (), {})()
        embed = type("E", (), {"title": "Trade", "colour": 1})()
        with pytest.raises(Exception, match="Could not update trade message"):
            await update_trade_msg(view, embed, "desc")

    async def test_successfully_update_trade_msg(self):
        view = type("V", (), {"msg_ref": SimpleNamespace(edit=AsyncMock())})()
        embed = type("E", (), {"title": "Trade", "colour": 1})()
        await update_trade_msg(view, embed, "desc")
        view.msg_ref.edit.assert_awaited_once()
