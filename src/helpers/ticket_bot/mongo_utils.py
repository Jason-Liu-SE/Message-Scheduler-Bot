import discord
from managers.pymongo_manager import PymongoManager


async def register_user_with_db(interaction: discord.Interaction) -> None:
    user = interaction.user
    userObj = await get_user_object(user.id)

    # creating a user for ticket tracking, if they don't exist
    try:
        if not userObj:
            await update_user_object(
                user.id,
                {"tickets": 0, "incoming_trades": [], "outgoing_trades": []},
            )
    except RuntimeError as e:
        raise Exception(e)


async def get_user_object(user_id: int) -> dict:
    return PymongoManager.find_in_collection_by_id("tickets", user_id)


async def update_user_object(user_id: int, data: dict) -> None:
    try:
        PymongoManager.update_collection("tickets", user_id, data)
    except RuntimeError as e:
        raise e
