from unittest.mock import AsyncMock

import pytest

from ui.common.dual_action import DualActionView
from ui.common.single_action import SingleActionView
from ui.common.ternary_action import TernaryActionView
from ui.common.view_wrapper import ViewWrapper
from ui.ticket_bot.confirm_action import ConfirmActionView
from tests.fakes.discord import FakeInteraction, FakeMember


@pytest.mark.unit
class TestViews:
    async def test_disable_children_edits_message_once(self):
        view = SingleActionView(label="Go")
        view.msg_ref = type("Msg", (), {"edit": AsyncMock()})()
        assert view.btn_action.disabled is False
        await view.disable_children()
        await view.disable_children()
        view.msg_ref.edit.assert_awaited_once()
        assert view.btn_action.disabled is True

    async def test_unauthorized_user_is_rejected(self):
        view = ViewWrapper(authorized_ids=[1])
        interaction = FakeInteraction(FakeMember(2, "Bob"))
        callback = AsyncMock()
        await view.handle_interaction(interaction, callback)
        callback.assert_not_awaited()
        interaction.response.defer.assert_awaited_once()
        embed = interaction.followup.send.await_args.kwargs["embed"]
        assert "permission" in embed.description

    async def test_authorized_user_runs_callback(self):
        view = ViewWrapper(authorized_ids=[1])
        interaction = FakeInteraction(FakeMember(1, "Alice"))
        callback = AsyncMock()
        await view.handle_interaction(interaction, callback)
        callback.assert_awaited_once()

    async def test_action_views_set_button_labels(self):
        single = SingleActionView(label="Preview")
        assert single.btn_action.label == "Preview"

        dual = DualActionView(primary_label="List", secondary_label="Reset")
        assert dual.btn_primary.label == "List"
        assert dual.btn_secondary.label == "Reset"

        ternary = TernaryActionView(
            primary_label="Ready",
            secondary_label="Un-ready",
            danger_label="Cancel",
        )
        assert ternary.btn_primary.label == "Ready"
        assert ternary.btn_secondary.label == "Un-ready"
        assert ternary.btn_danger.label == "Cancel"

        confirm = ConfirmActionView()
        assert confirm.btn_yes.label == "Yes"
        assert confirm.btn_no.label == "No"
