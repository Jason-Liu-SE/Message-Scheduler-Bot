from typing import Literal
from bson import ObjectId
import discord
from managers.pymongo_manager import PymongoManager


async def register_user_with_db(user: discord.Member) -> None:
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


async def get_ranked_user_objects(
    sort_field: str, direction: Literal["ASC", "DESC"], query: dict = {}, limit: int = 0
) -> dict:
    return PymongoManager.find_many_in_collection(
        "tickets", query, sort_field, direction, limit
    )


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


async def get_many_reward_objects(
    query: dict,
    sort_field: str | None = None,
    dir: Literal["ASC", "DESC"] = "ASC",
    limit: int = 0,
) -> dict:
    return PymongoManager.find_many_in_collection(
        "rewards", query, sort=sort_field, dir=dir, limit=limit
    )


async def get_reward_object(reward_id: ObjectId) -> dict:
    return PymongoManager.find_in_collection_by_id("rewards", reward_id)


async def update_reward_object(reward_id: ObjectId, data: dict) -> None:
    PymongoManager.update_collection("rewards", reward_id, data)


async def delete_reward_object(reward_id: ObjectId) -> None:
    PymongoManager.delete_by_id("rewards", reward_id)
