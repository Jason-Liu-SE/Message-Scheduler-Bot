import discord
from helpers import pymongo_manager


async def register_server_with_db(interaction: discord.Interaction) -> None:
    # instantiating a schedule and message collection entry if one doesn't exist
    msgObj = await get_message_object(interaction.message.guild.id)

    try:
        # adding the msgObj if a corresponding server doesn't already exist in the DB
        if not msgObj:
            await update_message_object(
                interaction.message.guild.id,
                {
                    "message": "",
                    "reactions": [],
                    "attachments": {"message_id": "", "channel_id": ""},
                },
            )
    except RuntimeError as e:
        raise Exception(e)


async def get_message_object(server_id: int) -> dict:
    return pymongo_manager.find_in_collection_by_id("messages", server_id)


async def get_schedule_by_server_id(server_id: int) -> dict:
    return pymongo_manager.find_all_in_collection("schedules", {"server_id": server_id})


async def get_post_by_id(post_id: int) -> dict:
    try:
        return pymongo_manager.find_in_collection_by_id("schedules", int(post_id))
    except RuntimeError as e:
        raise e


async def delete_post_by_id(post_id: int) -> None:
    try:
        pymongo_manager.delete_by_id("schedules", int(post_id))
    except RuntimeError as e:
        raise e


async def delete_server_posts(server_id: int) -> None:
    try:
        pymongo_manager.delete_all_by_query("schedules", {"server_id": server_id})
    except RuntimeError as e:
        raise e


async def update_message_object(server_id: int, data: dict) -> None:
    try:
        pymongo_manager.update_collection("messages", server_id, data)
    except RuntimeError as e:
        raise e


async def update_schedule(id: int, data: dict) -> None:
    try:
        pymongo_manager.update_collection("schedules", id, data)
    except RuntimeError as e:
        raise e
