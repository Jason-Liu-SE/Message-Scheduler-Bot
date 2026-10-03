from types import SimpleNamespace
from unittest.mock import AsyncMock

import discord


class FakeRole:
    def __init__(self, role_id: int, name: str):
        self.id = role_id
        self.name = name

    def __eq__(self, other):
        return isinstance(other, FakeRole) and self.id == other.id


class FakeMember:
    def __init__(
        self,
        user_id: int,
        name: str = "User",
        roles: list | None = None,
        colour: discord.Colour | None = None,
        bot: bool = False,
    ):
        self.id = user_id
        self.name = name
        self.display_name = name
        self.mention = f"<@{user_id}>"
        self.roles = roles or []
        self.colour = colour or discord.Colour.default()
        self.color = self.colour
        self.bot = bot
        self.display_avatar = SimpleNamespace(url="https://example.test/avatar.png")
        self.send = AsyncMock()


class FakeGuild:
    def __init__(
        self,
        guild_id: int = 100,
        name: str = "Test Guild",
        members: list | None = None,
        emojis: list | None = None,
    ):
        self.id = guild_id
        self.name = name
        self.members = members or []
        self.emojis = emojis or []
        self._members_by_id = {member.id: member for member in self.members}

    def get_member(self, user_id: int):
        return self._members_by_id.get(user_id)


class FakeChannel:
    def __init__(self, channel_id: int = 200, name: str = "general"):
        self.id = channel_id
        self.name = name
        self.send = AsyncMock(return_value=SimpleNamespace(id=999, add_reaction=AsyncMock()))
        self.fetch_message = AsyncMock()
        self.history = AsyncMock()


class FakeInteraction:
    def __init__(
        self,
        user: FakeMember,
        guild: FakeGuild | None = None,
        channel: FakeChannel | None = None,
    ):
        self.user = user
        self.guild = guild or FakeGuild(members=[user])
        self.channel = channel or FakeChannel()
        self.response = SimpleNamespace(
            defer=AsyncMock(),
            send_message=AsyncMock(),
        )
        self.followup = SimpleNamespace(send=AsyncMock())
        self.original_response = AsyncMock(
            return_value=SimpleNamespace(edit=AsyncMock(), id=1)
        )
