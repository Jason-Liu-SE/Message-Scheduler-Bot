from types import SimpleNamespace

import pytest

from helpers.validate import (
    filter_valid_kwargs,
    has_role,
    is_development,
    validate_channel,
)


@pytest.mark.unit
class TestValidateChannel:
    def test_accepts_numeric_channel(self):
        validate_channel("123456789")

    def test_rejects_non_numeric_channel(self):
        with pytest.raises(ValueError, match="numerical value"):
            validate_channel("#general")


@pytest.mark.unit
class TestIsDevelopment:
    def test_true_when_env_is_true(self, monkeypatch):
        monkeypatch.setenv("IS_DEV", "True")
        assert is_development() is True

    def test_false_when_env_missing_or_false(self, monkeypatch):
        monkeypatch.delenv("IS_DEV", raising=False)
        assert is_development() is False
        monkeypatch.setenv("IS_DEV", "false")
        assert is_development() is False


@pytest.mark.unit
class TestHasRole:
    def test_matches_role_name_case_insensitively(self):
        interaction = SimpleNamespace(
            user=SimpleNamespace(roles=[SimpleNamespace(id=1, name="Moderator")])
        )
        assert has_role(interaction, ["moderator"]) is True

    def test_matches_role_id(self):
        interaction = SimpleNamespace(
            user=SimpleNamespace(roles=[SimpleNamespace(id=99, name="Other")])
        )
        assert has_role(interaction, [99]) is True

    def test_returns_false_without_match(self):
        interaction = SimpleNamespace(
            user=SimpleNamespace(roles=[SimpleNamespace(id=1, name="Member")])
        )
        assert has_role(interaction, ["Admin"]) is False
        assert has_role(interaction, [2]) is False
