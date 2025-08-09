from typing import Awaitable, Callable
import discord

from helpers.command_helper import catch_and_log
from helpers.message_utils import send_error


class ViewWrapper(discord.ui.View):
    def __init__(self, timeout: float | None = 60.0, authorized_ids: list[int] = []):
        super().__init__(timeout=timeout)

        # reference to the message containing this View
        self.msg_ref: discord.InteractionMessage | None = None

        # a list of ids that have authorization to use the view
        self.authorized_ids = authorized_ids

    async def on_timeout(self):
        await self.disable_children()

    async def disable_children(self) -> None:
        for child in self.children:
            if hasattr(child, "disabled"):
                child.disabled = True

        # update message
        if self.msg_ref:
            await self.msg_ref.edit(view=self)

    async def handle_interaction(
        self,
        interaction: discord.Interaction,
        callback: (
            Callable[[discord.Interaction, discord.ui.View], Awaitable[None]] | None
        ),
        *args
    ) -> bool:
        @catch_and_log(interaction=interaction)
        async def run_callback() -> None:
            if callback:
                await callback(interaction, self, *args)

        await interaction.response.defer()

        if (
            len(self.authorized_ids) > 0
            and interaction.user.id not in self.authorized_ids
        ):
            await send_error(
                interaction,
                "You do not have permission to perform this action.",
                ephemeral=True,
            )
        else:
            await run_callback()
