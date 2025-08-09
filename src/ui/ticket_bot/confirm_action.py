from typing import Awaitable, Callable
import discord

from ui.common.view_wrapper import ViewWrapper


class ConfirmActionView(ViewWrapper):
    def __init__(
        self,
        timeout: int = 60,
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
        await self.handle_interaction(interaction, self.handle_yes, btn)

    @discord.ui.button(label="No", style=discord.ButtonStyle.gray)
    async def btn_no(
        self, interaction: discord.Interaction, btn: discord.ui.Button
    ) -> None:
        await self.handle_interaction(interaction, self.handle_no, btn)

    #########################################################################################
    ##################################### Handlers ##########################################
    #########################################################################################
    async def handle_yes(
        self, interaction: discord.Interaction, btn: discord.ui.Button
    ) -> None:
        await self.disable_children()
        if self.accept_cb:
            await self.accept_cb(interaction, btn)

    async def handle_no(
        self, interaction: discord.Interaction, btn: discord.ui.Button
    ) -> None:
        await self.disable_children()
        if self.reject_cb:
            await self.reject_cb(interaction, btn)
