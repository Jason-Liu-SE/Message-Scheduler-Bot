from datetime import datetime
import discord
from managers.pymongo_manager import *


async def register_server_with_db(interaction: discord.Interaction) -> None:
    # instantiating a schedule and message collection entry if one doesn't exist
    msgObj = await get_message_object(interaction.guild.id)

    try:
        # adding the msgObj if a corresponding server doesn't already exist in the DB
        if not msgObj:
            await update_message_object(
                interaction.guild.id,
                {
                    "message": "",
                    "reactions": [],
                    "attachments": {"message_id": "", "channel_id": ""},
                },
            )
    except RuntimeError as e:
        raise Exception(e)


async def get_message_object(server_id: int) -> dict:
    return PymongoManager.find_in_collection_by_id("messages", server_id)


async def get_schedule_by_server_id(server_id: int) -> dict:
    return PymongoManager.find_all_in_collection("schedules", {"server_id": server_id})


async def get_post_by_id(post_id: int | ObjectId) -> dict:
    try:
        return PymongoManager.find_in_collection_by_id("schedules", post_id)
    except RuntimeError as e:
        raise e


async def delete_post_by_id(post_id: int | ObjectId) -> None:
    try:
        PymongoManager.delete_by_id("schedules", post_id)
    except RuntimeError as e:
        raise e


async def delete_server_posts(server_id: int) -> None:
    try:
        PymongoManager.delete_all_by_query("schedules", {"server_id": server_id})
    except RuntimeError as e:
        raise e


async def update_message_object(server_id: int, data: dict) -> None:
    try:
        PymongoManager.update_collection("messages", server_id, data)
    except RuntimeError as e:
        raise e


async def update_schedule(post_id: int | ObjectId, data: dict) -> None:
    try:
        PymongoManager.update_collection("schedules", post_id, data)
    except RuntimeError as e:
        raise e


def get_posts_in_date_range(start: datetime, end: datetime) -> list:
    try:
        return PymongoManager.find_in_range("schedules", "time", start, end)
    except:
        raise RuntimeError(
            f"ERROR: Failed to retrieve entries in collection 'schedules' for date range {start} to {end}"
        )
