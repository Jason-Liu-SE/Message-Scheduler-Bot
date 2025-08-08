from typing import Any, Callable
import discord

from helpers.message_utils import send_error


class ViewWrapper(discord.ui.View):
    def __init__(self, timeout: int = 60, author: int = None):
        super().__init__(timeout=timeout)

        # reference to the message containing this View
        self.msg_ref: discord.InteractionMessage | None = None

        # id of some user
        self.author: int | None = author

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
        callback: Callable[[discord.Interaction], Any],
        *args
    ) -> bool:
        await interaction.response.defer()

        if self.author and self.author != interaction.user.id:
            await send_error(
                interaction,
                "You do not have permission to perform this action.",
                ephemeral=True,
            )
        else:
            await callback(interaction, *args)
