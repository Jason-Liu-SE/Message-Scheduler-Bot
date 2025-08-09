from typing import Awaitable, Callable
import discord

from ui.common.view_wrapper import ViewWrapper


class SingleActionView(ViewWrapper):
    def __init__(
        self,
        label: str = "Action",
        style: discord.ButtonStyle = discord.ButtonStyle.primary,
        timeout: int = None,
        action_cb: (
            Callable[[discord.Interaction, discord.ui.Button], Awaitable[None]] | None
        ) = None,
        authorized_ids: list[int] = [],
    ):
        super().__init__(timeout=timeout, authorized_ids=authorized_ids)

        self.action_cb = action_cb
        self.btn_action.label = label
        self.btn_action.style = style

    #########################################################################################
    ################################## Interactables ########################################
    #########################################################################################
    @discord.ui.button(label="Change Me", style=discord.ButtonStyle.primary)
    async def btn_action(
        self, interaction: discord.Interaction, btn: discord.ui.Button
    ) -> None:
        await self.handle_interaction(interaction, self.handle_action, btn)

    #########################################################################################
    ##################################### Handlers ##########################################
    #########################################################################################
    async def handle_action(
        self, interaction: discord.Interaction, btn: discord.ui.Button
    ) -> None:
        await self.disable_children()
        self.timeout = 30
        if self.action_cb:
            await self.action_cb(interaction, btn)
