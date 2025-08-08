import discord


class ViewWrapper(discord.ui.View):
    def __init__(self, timeout: int = 60):
        super().__init__(timeout=timeout)

        # reference to the message containing this View
        self.msg_ref: discord.InteractionMessage | None = None

    async def on_timeout(self):
        await self.disable_children()

    async def disable_children(self) -> None:
        for child in self.children:
            if hasattr(child, "disabled"):
                child.disabled = True

        # update message
        if self.msg_ref:
            await self.msg_ref.edit(view=self)
