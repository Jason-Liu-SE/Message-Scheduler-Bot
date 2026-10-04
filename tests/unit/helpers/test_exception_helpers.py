from unittest.mock import AsyncMock

import pytest

from helpers.exception_helpers import handle_error
from tests.fakes.discord import FakeInteraction, FakeMember


@pytest.mark.unit
async def test_handle_error_logs_and_notifies_user(quiet_logger):
    interaction = FakeInteraction(FakeMember(1))
    await handle_error(interaction, "Failed to save", RuntimeError("db down"))
    embed = interaction.followup.send.await_args.kwargs["embed"]
    quiet_logger.error.assert_called_once_with("Failed to save: db down")
    assert embed.title == "ERROR"
    assert embed.description == "Failed to save"
