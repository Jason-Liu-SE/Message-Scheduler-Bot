from typing import Awaitable, Callable
import discord

from ui.common.view_wrapper import ViewWrapper


class ConfirmActionView(ViewWrapper):
    def __init__(
        self,
        timeout: float | None = 60.0,
        accept_cb: (
            Callable[[discord.Interaction, discord.ui.Button], Awaitable[None]] | None
        ) = None,
        reject_cb: (
            Callable[[discord.Interaction, discord.ui.Button], Awaitable[None]] | None
        ) = None,
        authorized_ids: list[int] = [],
    ):
        super().__init__(timeout=timeout, authorized_ids=authorized_ids)

        self.accept_cb = accept_cb
        self.reject_cb = reject_cb

    #########################################################################################
    ################################## Interactables ########################################
    #########################################################################################
    @discord.ui.button(label="Yes", style=discord.ButtonStyle.primary)
    async def btn_yes(
        self, interaction: discord.Interaction, btn: discord.ui.Button
    ) -> None:
        await self.handle_interaction(interaction, self.accept_cb, btn)

    @discord.ui.button(label="No", style=discord.ButtonStyle.gray)
    async def btn_no(
        self, interaction: discord.Interaction, btn: discord.ui.Button
    ) -> None:
        await self.handle_interaction(interaction, self.reject_cb, btn)
