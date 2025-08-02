from helpers import pymongo_manager


async def registerServerWithDB(ctx):
    # instantiating a schedule and message collection entry if one doesn't exist
    msgObj = await getMessageObject(ctx)

    try:
        # adding the msgObj if a corresponding server doesn't already exist in the DB
        if not msgObj:
            await updateMessageObject(
                ctx,
                {
                    "message": "",
                    "reactions": [],
                    "attachments": {"message_id": "", "channel_id": ""},
                },
            )
    except RuntimeError as e:
        raise Exception(e)


async def getMessageObject(ctx):
    return pymongo_manager.find_in_collection_by_id("messages", ctx.message.guild.id)


async def getScheduleByServerId(serverID):
    return pymongo_manager.find_all_in_collection("schedules", {"server_id": serverID})


async def getPostById(postID: int):
    try:
        return pymongo_manager.find_in_collection_by_id("schedules", int(postID))
    except RuntimeError as e:
        raise e


async def deletePostById(postID: int):
    try:
        pymongo_manager.delete_by_id("schedules", int(postID))
    except RuntimeError as e:
        raise e


async def deleteServerPosts(serverID):
    try:
        pymongo_manager.delete_all_by_query("schedules", {"server_id": serverID})
    except RuntimeError as e:
        raise e


async def updateMessageObject(ctx, data):
    try:
        pymongo_manager.update_collection("messages", ctx.message.guild.id, data)
    except RuntimeError as e:
        raise e


async def updateSchedule(id, data):
    try:
        pymongo_manager.update_collection("schedules", id, data)
    except RuntimeError as e:
        raise e
