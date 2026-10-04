import pytest

from helpers.keep_alive import home
from helpers.validate import is_development


@pytest.mark.unit
def test_home_returns_pong(monkeypatch, quiet_logger):
    monkeypatch.setenv("IS_DEV", "false")
    assert home() == "Pong"
    quiet_logger.info.assert_not_called()


@pytest.mark.unit
def test_home_logs_in_development(monkeypatch, quiet_logger):
    monkeypatch.setenv("IS_DEV", "true")
    assert is_development() is True
    assert home() == "Pong"
    quiet_logger.info.assert_called_once()

    assert 0 == 1
