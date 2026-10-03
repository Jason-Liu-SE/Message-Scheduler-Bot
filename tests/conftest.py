from unittest.mock import MagicMock

import pytest

from managers.pymongo_manager import PymongoManager
from tests.fakes.discord import (
    FakeChannel,
    FakeGuild,
    FakeInteraction,
    FakeMember,
    FakeRole,
)
from tests.fakes.mongo import FakeDB


@pytest.fixture(autouse=True)
def quiet_logger(monkeypatch):
    logger = MagicMock()
    monkeypatch.setattr("helpers.logger.Logger.info", logger.info)
    monkeypatch.setattr("helpers.logger.Logger.warn", logger.warn)
    monkeypatch.setattr("helpers.logger.Logger.error", logger.error)
    monkeypatch.setattr("helpers.logger.Logger.exception", logger.exception)
    monkeypatch.setattr("helpers.logger.Logger.traceback", logger.traceback)
    return logger


@pytest.fixture
def fake_db():
    db = FakeDB()
    PymongoManager._db = db
    yield db
    PymongoManager._db = None


@pytest.fixture
def make_member():
    def _make(user_id=1, name="Alice", roles=None, **kwargs):
        return FakeMember(user_id=user_id, name=name, roles=roles or [], **kwargs)

    return _make


@pytest.fixture
def make_interaction(make_member):
    def _make(
        user=None,
        guild=None,
        roles=None,
        guild_id=100,
        extra_members=None,
    ):
        member = user or make_member(roles=roles)
        members = [member, *(extra_members or [])]
        guild = guild or FakeGuild(guild_id=guild_id, members=members)
        return FakeInteraction(user=member, guild=guild)

    return _make


@pytest.fixture
def moderator_role():
    return FakeRole(807340774781878333, "Moderator")


@pytest.fixture
def everyone_role():
    return FakeRole(807335525798117407, "@everyone")
