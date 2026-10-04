from unittest.mock import AsyncMock, patch

import pytest

from helpers.ticket_bot.autofill_helpers import get_reward_choices


@pytest.mark.unit
async def test_get_reward_choices_trims_input_and_formats_matching_rewards():
    rewards = {
        "abc123": {
            "name": "Blue Sticker 123456789123456789123456789123456789123456789"
        },
        "def456": {"name": "A very long reward name that is truncated"},
        "zzz999": {"name": "Other"},
    }

    with patch(
        "helpers.ticket_bot.autofill_helpers.get_many_reward_objects",
        new=AsyncMock(return_value=rewards),
    ) as get_rewards:
        choices = await get_reward_choices(None, "  BLUE  ")

    get_rewards.assert_awaited_once()
    assert [(choice.name, choice.value) for choice in choices] == [
        ("abc123 | Blue Sticker 12345678912345678", "abc123")
    ]


@pytest.mark.unit
async def test_get_reward_choices_matches_ids_case_insensitively_and_truncates_names():
    reward_id_1 = "AbC123"
    reward_id_2 = "9123AbC"
    rewards = {
        reward_id_1: {
            "name": "A reward whose name is definitely longer than thirty chars"
        },
        reward_id_2: {
            "name": "2 reward whose name is definitely longer than thirty chars"
        },
        "other": {"name": "Unrelated"},
    }

    with patch(
        "helpers.ticket_bot.autofill_helpers.get_many_reward_objects",
        new=AsyncMock(return_value=rewards),
    ):
        choices = await get_reward_choices(None, "abc")

    assert len(choices) == 2
    assert choices[0].value == reward_id_1
    assert choices[0].name == f"{reward_id_1} | A reward whose name is definit"
    assert choices[1].value == reward_id_2
    assert choices[1].name == f"{reward_id_2} | 2 reward whose name is definit"


@pytest.mark.unit
async def test_get_reward_choices_returns_no_choices_when_nothing_matches():
    with patch(
        "helpers.ticket_bot.autofill_helpers.get_many_reward_objects",
        new=AsyncMock(
            return_value={
                "zzz999": {"name": "Other"},
            }
        ),
    ):
        choices = await get_reward_choices(None, "missing")

    assert choices == []
