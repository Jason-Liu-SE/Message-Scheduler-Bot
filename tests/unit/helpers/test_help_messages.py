import pytest

from helpers.help_messages import (
    MS_HELP_MSGS,
    TICKET_BOT_ADMIN_HELP_MSGS,
    TICKET_BOT_HELP_MSGS,
    _load_help_messages,
)
from helpers.help_messages import MS_HELP_PATH


@pytest.mark.unit
class TestHelpMessages:
    def test_nested_command_filenames_become_spaced_keys(self):
        assert "rewards list" in TICKET_BOT_HELP_MSGS
        assert "rewards_list" not in TICKET_BOT_HELP_MSGS

    def test_description_loaded_for_each_bot(self):
        assert "description" in MS_HELP_MSGS
        assert "description" in TICKET_BOT_HELP_MSGS
        assert "description" in TICKET_BOT_ADMIN_HELP_MSGS
        assert len(MS_HELP_MSGS["description"]) > 0
        assert len(TICKET_BOT_HELP_MSGS["description"]) > 0
        assert len(TICKET_BOT_ADMIN_HELP_MSGS["description"]) > 0

    def test_loader_reads_markdown_files(self):
        loaded = _load_help_messages(MS_HELP_PATH)
        assert loaded == MS_HELP_MSGS
