from datetime import datetime, timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from helpers.command_helper import (
    catch_and_log,
    generate_autocomplete,
    handle_command,
    sort_schedules_by_date,
)


@pytest.mark.unit
class TestSortSchedulesByDate:
    def test_sorts_ascending_by_time(self):
        now = datetime(2026, 1, 1)
        schedule = {
            "b": {"time": now + timedelta(hours=2), "message": "later"},
            "a": {"time": now + timedelta(hours=1), "message": "sooner"},
            "c": {"time": now + timedelta(hours=3), "message": "even later"},
        }
        ordered = list(sort_schedules_by_date(schedule))
        assert ordered == ["a", "b", "c"]

    def test_sorts_descending(self):
        now = datetime(2026, 1, 1)
        schedule = {
            "a": {"time": now + timedelta(hours=1)},
            "b": {"time": now + timedelta(hours=2)},
            "c": {"time": now + timedelta(hours=3)},
        }
        ordered = list(sort_schedules_by_date(schedule, is_ascending=False))
        assert ordered == ["c", "b", "a"]


@pytest.mark.unit
class TestGenerateAutocomplete:
    async def test_filters_items_and_respects_limit(self):
        autocomplete = generate_autocomplete(
            list(range(1, 40)), const_items={"clear": "clear"}
        )
        choices = await autocomplete(SimpleNamespace(), "1")
        assert choices[0].name == "clear"
        assert all(
            "1" in str(choice.value) or choice.value == "clear" for choice in choices
        )
        assert len(choices) <= 25

    async def test_appends_callback_choices_when_under_limit(self):
        async def extra(_interaction, current):
            return [SimpleNamespace(name=f"extra-{current}", value="extra")]

        autocomplete = generate_autocomplete(["alpha"], extra)
        choices = await autocomplete(SimpleNamespace(), "z")
        assert [choice.value for choice in choices] == ["extra"]


@pytest.mark.unit
class TestCatchAndLog:
    async def test_sends_value_error_to_user(self):
        interaction = SimpleNamespace()
        send_error = AsyncMock()

        @catch_and_log(interaction)
        async def raise_error():
            raise ValueError("bad")

        with pytest.MonkeyPatch.context() as mp:
            mp.setattr("helpers.command_helper.send_error", send_error)
            await raise_error()

        send_error.assert_awaited_once()
        assert str(send_error.await_args.args[1]) == "bad"

    async def test_generic_errors_send_fallback_message(self):
        interaction = SimpleNamespace()
        send_error = AsyncMock()

        @catch_and_log(interaction)
        async def raise_error():
            raise RuntimeError("bad")

        with pytest.MonkeyPatch.context() as mp:
            mp.setattr("helpers.command_helper.send_error", send_error)
            await raise_error()

        send_error.assert_awaited_once_with(interaction, "An error occurred.")


@pytest.mark.unit
class TestHandleCommand:
    async def test_defers_and_rejects_missing_role(self):
        interaction = SimpleNamespace(
            response=SimpleNamespace(defer=AsyncMock()),
            user=SimpleNamespace(mention="<@1>", roles=[]),
        )
        send_error = AsyncMock()
        cmd = AsyncMock()

        with pytest.MonkeyPatch.context() as mp:
            mp.setattr("helpers.command_helper.send_error", send_error)
            await handle_command(cmd, interaction, ["Admin"])

        interaction.response.defer.assert_awaited_once()
        send_error.assert_awaited_once()
        cmd.assert_not_awaited()

    async def test_runs_command_when_role_matches(self):
        interaction = SimpleNamespace(
            response=SimpleNamespace(defer=AsyncMock()),
            user=SimpleNamespace(
                mention="<@1>",
                roles=[SimpleNamespace(id=1, name="Admin")],
            ),
        )
        cmd = AsyncMock()
        await handle_command(cmd, interaction, ["Admin"], "self", interaction, extra=1)
        cmd.assert_awaited_once()
