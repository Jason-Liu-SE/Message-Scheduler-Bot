from pathlib import Path

MS_HELP_PATH = Path(__file__).resolve().parents[1] / "data/help/message_scheduler"
TICKET_BOT_HELP_PATH = Path(__file__).resolve().parents[1] / "data/help/ticket_bot"
TICKET_BOT_ADMIN_HELP_PATH = (
    Path(__file__).resolve().parents[1] / "data/help/ticket_bot_admin"
)


def _load_help_messages(help_path: Path) -> dict[str, str]:
    messages = {}

    for message_path in sorted(help_path.glob("*.md")):
        key = message_path.stem.replace("_", " ")
        messages[key] = message_path.read_text(encoding="utf-8")

    return messages


MS_HELP_MSGS = _load_help_messages(MS_HELP_PATH)
TICKET_BOT_HELP_MSGS = _load_help_messages(TICKET_BOT_HELP_PATH)
TICKET_BOT_ADMIN_HELP_MSGS = _load_help_messages(TICKET_BOT_ADMIN_HELP_PATH)
