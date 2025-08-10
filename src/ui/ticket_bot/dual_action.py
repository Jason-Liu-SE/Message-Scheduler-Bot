from typing import Awaitable, Callable
import discord

from ui.common.view_wrapper import ViewWrapper


class DualActionView(ViewWrapper):
    def __init__(
        self,
        timeout: int = 60,
        primary_label: str = "Primary",
        secondary_label: str = "Secondary",
        primary_style: discord.ButtonStyle = discord.ButtonStyle.primary,
        secondary_style: discord.ButtonStyle = discord.ButtonStyle.secondary,
        primary_cb: (
            Callable[
                [discord.Interaction, discord.ui.View, discord.ui.Button],
                Awaitable[None],
            ]
            | None
        ) = None,
        secondary_cb: (
            Callable[
                [discord.Interaction, discord.ui.View, discord.ui.Button],
                Awaitable[None],
            ]
            | None
        ) = None,
        authorized_ids: list[int] = [],
    ):
        super().__init__(timeout=timeout, authorized_ids=authorized_ids)

        self.primary_cb = primary_cb
        self.secondary_cb = secondary_cb

        self.btn_primary.label = primary_label
        self.btn_secondary.label = secondary_label

        self.btn_primary.style = primary_style
        self.btn_secondary.style = secondary_style

    #########################################################################################
    ################################## Interactables ########################################
    #########################################################################################
    @discord.ui.button(label="Primary", style=discord.ButtonStyle.primary)
    async def btn_primary(
        self, interaction: discord.Interaction, btn: discord.ui.Button
    ) -> None:
        await self.handle_interaction(interaction, self.primary_cb, btn)

    @discord.ui.button(label="Secondary", style=discord.ButtonStyle.secondary)
    async def btn_secondary(
        self, interaction: discord.Interaction, btn: discord.ui.Button
    ) -> None:
        await self.handle_interaction(interaction, self.secondary_cb, btn)
