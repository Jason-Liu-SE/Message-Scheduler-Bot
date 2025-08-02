from functools import cmp_to_key
import discord
from helpers.message_utils import *
from helpers.validate import *
from helpers.time import *
from helpers.message_utils import *
from helpers.message_scheduler.mongo_utils import *


async def handle_print(ctx, bot, channel=None, post_id=None):
    # determining which message object to use
    if not post_id:
        message_obj = await get_message_object(ctx)
    else:
        schedule = await get_schedule_by_server_id(ctx.message.guild.id)

        if int(post_id) not in schedule.keys():
            raise ValueError(f"Could not find a post with post ID: {post_id}")

        message_obj = schedule[int(post_id)]

    # adding attachments
    attachments = []

    try:
        if message_obj["attachments"]["message_id"] != "":
            msg = await ctx.fetch_message(message_obj["attachments"]["message_id"])

            for f in msg.attachments:
                file = await f.to_file()
                attachments.append(file)
    except Exception as e:
        print(e)

    # sending the message
    try:
        msg = await send_message(ctx, bot, message_obj["message"], channel, attachments)
    except RuntimeError as e:
        raise e
    except ValueError as e:
        raise e

    # adding emojis
    for reaction in message_obj["reactions"]:
        try:
            # set to a custom emoji by default
            emoji = discord.utils.get(ctx.message.guild.emojis, name=reaction)

            if not emoji:  # standard emojis
                emoji = reaction

            await msg.add_reaction(emoji)
        except:
            print(f"Unknown emoji: {reaction}")


async def handle_add(ctx, rawArgs):
    date_format = "%d/%m/%YT%H:%M:%S%z"

    # argument validation
    args = rawArgs.strip().split(" ")

    try:
        if len(args) != 3:
            raise ValueError("Please provide exactly 3 arguments to the 'add' command.")

        await validate_channel(args[0])
        await validate_date({"date": args[1], "time": args[2]})
    except ValueError as e:
        raise e

    # formatting the data
    channel = int(args[0])
    date_obj = datetime.strptime(args[1] + "T" + args[2] + ":00+00:00", date_format)

    # validating the user's desired time
    try:
        await validate_time(date_obj)
    except ValueError as e:
        raise e

    # getting stored message
    msg_obj = await get_message_object(ctx)

    # no message was set
    if msg_obj["message"] == "":
        raise ValueError("No message was set! This command was ignored.")

    # setting the postID to the message id of the message that called the 'add' command
    post_id = ctx.message.id

    # db updates
    try:
        schedule_data = {
            "server_id": ctx.message.guild.id,
            "channel": channel,
            "message": msg_obj["message"],
            "reactions": msg_obj["reactions"],
            "attachments": msg_obj["attachments"],
            "time": date_obj,
        }
    except Exception as e:
        print(e)

    try:
        # schedule the current message
        await update_schedule(post_id, schedule_data)
    except RuntimeError as e:
        print(e)
        raise RuntimeError("Could not add the message to the schedule.")

    try:
        # reset the current message
        await update_message_object(
            ctx,
            {
                "message": "",
                "reactions": [],
                "attachments": {"message_id": "", "channel_id": ""},
            },
        )
    except:
        print(e)
        raise RuntimeError("Schedule updated, but the message was not reset.")

    # informing the user
    await send_embedded_message(
        ctx,
        0x00FF00,
        {
            "title": "Success",
            "desc": f"Message added to post schedule!\n\n**Post ID**: {post_id}",
        },
    )


async def handle_remove(ctx, msg):
    post_id = msg.strip().split(" ")[0]

    if not post_id.isdigit():
        raise TypeError(
            f"Invalid post ID: {post_id}. Post IDs may only contain numbers."
        )

    post = await get_post_by_id(int(post_id))

    # no scheduled post corresponds with the provided one
    if not post:
        raise ValueError(
            f"There is no scheduled post with the corresponding post ID: {post_id}"
        )

    # deleting the msg
    try:
        await delete_post_by_id(int(post_id))
    except RuntimeError as e:
        print(e)
        raise RuntimeError(
            f"Could not delete the post with ID: {post_id}. The command will be ignored."
        )

    await send_embedded_message(
        ctx,
        0x00FF00,
        {
            "title": "Success",
            "desc": f"Post with ID {post_id} was removed from the post schedule!",
        },
    )


async def handle_set(ctx, msg):
    msg_obj = await get_message_object(ctx)
    msg_obj["message"] = msg
    msg_obj["attachments"] = {
        "message_id": ctx.message.id,
        "channel_id": ctx.message.channel.id,
    }

    await update_message_object(ctx, msg_obj)

    # no text was provided
    if msg == "":
        await send_embedded_message(
            ctx, 0x00FF00, {"title": "Success", "desc": "The message was cleared!"}
        )
        return

    await send_embedded_message(
        ctx, 0x00FF00, {"title": "Success", "desc": "The message has been set!"}
    )


async def handle_set_reaction(ctx, msg):
    emojis = msg.strip().split(" ")

    msg_obj = await get_message_object(ctx)

    msg_obj["reactions"] = emojis

    await update_message_object(ctx, msg_obj)

    # no emojis specified
    if len(emojis) == 1 and emojis[0] == "":
        await send_embedded_message(
            ctx, 0x00FF00, {"title": "Success", "desc": f"Reactions were cleared!"}
        )
        return

    await send_embedded_message(
        ctx,
        0x00FF00,
        {"title": "Success", "desc": f"Reaction(s) {msg} added to message!"},
    )


async def handle_reset(ctx):
    try:
        await update_message_object(
            ctx,
            {
                "message": "",
                "reactions": [],
                "attachments": {"message_id": "", "channel_id": ""},
            },
        )
    except RuntimeError as e:
        print(e)
        raise RuntimeError(f"Could not reset the message. The command will be ignored.")

    await send_embedded_message(
        ctx, 0x00FF00, {"title": "Success", "desc": "The message has been reset!"}
    )


async def handle_clear(ctx):
    try:
        await delete_server_posts(ctx.message.guild.id)
    except RuntimeError as e:
        print(e)
        raise RuntimeError(
            f"Could not delete all scheduled posts for this server. This command will be ignored."
        )

    await send_embedded_message(
        ctx, 0x00FF00, {"title": "Success", "desc": "The post schedule was cleared!"}
    )


async def handle_preview(ctx, bot, rawArgs):
    # getting the type of print operation
    args = rawArgs.strip().split(" ")

    postType = args[0]

    if len(args) != 1 or (postType != "current" and not postType.isdigit()):
        raise ValueError("The provided arguments are invalid. Command will be ignored.")

    # determining which message to print
    try:
        if postType == "current":
            await handle_print(ctx, bot)
        else:
            await handle_print(ctx, bot, post_id=postType)
    except RuntimeError as e:
        raise e
    except ValueError as e:
        raise e


async def handle_list(ctx):
    schedule = await get_schedule_by_server_id(ctx.message.guild.id)

    # no scheduled posts
    if not schedule or len(schedule) == 0:
        await send_embedded_message(
            ctx,
            0xFFFF00,
            {"title": "Warning", "desc": f"You don't have any scheduled posts!"},
        )
        return

    # returning a list of the schedule
    msg = ""
    msg_list = []

    sorted_items = dict(
        sorted(
            schedule.items(),
            key=cmp_to_key(lambda a, b: 1 if a[1]["time"] > b[1]["time"] else -1),
        )
    )

    for index, post_id in enumerate(sorted_items):
        msg += (
            f"**#{index + 1}**\n"
            f"**Post ID**: {post_id}\n"
            f"**Post Time**: {schedule[post_id]['time']}\n"
            f"**Preview**: {schedule[post_id]['message'] if len(schedule[post_id]['message']) < 50 else schedule[post_id]['message'][0:47] + '...'}\n\n"
        )

        if len(msg) > 1500:
            msg_list.append(msg)
            msg = ""

    msg_list.append(msg)

    for message in msg_list:
        await send_embedded_message(ctx, 0x00FF00, {"title": "Posts", "desc": message})


async def handle_help(ctx):
    help_desc = """The Message Scheduler is used to schedule your posts based on the message that you set via the 'set' command (and any modifications made with appropriate commands. E.g. 'reaction'). If you don't like your message, you can override it with another message via the 'set' command, or if you have made other modifications to the message (e.g. via 'reaction'), you can use the 'reset' command to reset the message entirely.
Once you are happy with the message, you can schedule it via the 'add' command. If you want to delete the message after it has been scheduled, simply use the 'remove' command with the ID that you were provided when the messaged was scheduled.
    
The commands are as follows:"""

    add_msg = """Adds the created message to the schedule. Note that a message must be created before it can be added to the schedule, times are specified in UTC, and you can only schedule posts for the future (e.g. if the time is 5:04, you can't schedule a post for any time prior to or equal to 5:04).
    
BTW:
UTC Time = EDT Time + 4 hours
UTC Time = EST Time + 5 hours
    
Format: !ms add <channel> <post date> <post time>
    
E.g. !ms add 1143322446909407323 30/01/2023 23:59
This would post the message on January 30, 2023 at 11:59 PM to the channel with ID 1143322446909407323"""

    remove_msg = """Removes a message from the schedule based on a post ID.
    
Format: !ms remove <message post id>
    
E.g. !ms remove 123"""

    set_msg = """Sets the message to be scheduled.
    
Format: !ms set <message>
    
E.g. !ms set This is an announcement"""

    reaction_msg = """Sets the reactions for the message.
    
Format: !ms reaction [<emoji>]
    
E.g. !ms reaction 😄 😢 🥯"""

    reset_msg = """Resets the message and all modifications made to it
    
Format: !ms reset
    
E.g. !ms reset"""

    clear_msg = """Un-schedules all previously scheduled messages
    
Format: !ms clearSchedule
    
E.g. !ms clearSchedule"""

    preview_msg = """Displays either the message that is currently being worked on or a particular scheduled post.
    
Format: !ms preview <current|post ID>
    
E.g. !ms preview current"""

    list_msg = """Lists all the currently scheduled messages, with their postID, post time, and a preview of their content.
    
Format: !ms list
    
E.g. !ms list"""

    fields = [
        {"name": "add", "value": add_msg},
        {"name": "remove", "value": remove_msg},
        {"name": "set", "value": set_msg},
        {"name": "reaction", "value": reaction_msg},
        {"name": "reset", "value": reset_msg},
        {"name": "clearSchedule", "value": clear_msg},
        {"name": "preview", "value": preview_msg},
        {"name": "list", "value": list_msg},
    ]

    await send_embedded_message(
        ctx,
        0x7E42F5,
        {"title": "Message Scheduler Commands", "desc": help_desc},
        fields,
    )
