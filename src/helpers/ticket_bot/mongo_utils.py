import discord
from managers.pymongo_manager import PymongoManager


async def register_user_with_db(interaction: discord.Interaction) -> None:
    user = interaction.user
    userObj = await get_user_object(user.id)

    # creating a user for ticket tracking, if they don't exist
    if not userObj:
        await update_user_object(
            user.id,
            {"tickets": 0, "incoming_trades": [], "outgoing_trades": []},
        )


async def get_user_object(user_id: int) -> dict:
    return PymongoManager.find_in_collection_by_id("tickets", user_id)


async def get_user_objects(user_ids: list[int]) -> dict:
    return PymongoManager.find_many_in_collection("tickets", {"_id": {"$in": user_ids}})


async def get_all_user_objects() -> dict:
    return PymongoManager.find_many_in_collection("tickets")


async def update_user_object(user_id: int, data: dict) -> None:
    PymongoManager.update_collection("tickets", user_id, data)


async def update_user_objects(user_objs: dict[int, dict]) -> None:
    for key, value in user_objs.items():
        PymongoManager.update_collection("tickets", key, value)


async def create_user_objects(user_ids: list[int]) -> None:
    for user_id in user_ids:
        PymongoManager.update_collection_on_insert(
            "tickets",
            user_id,
            {"tickets": 0, "incoming_trades": [], "outgoing_trades": []},
        )
