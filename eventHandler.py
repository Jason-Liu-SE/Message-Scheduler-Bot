import pymongoManager
import discord
from datetime import datetime, timedelta, timezone
import math
import asyncio
from discord.ext import tasks

bot = None

#####################################################################
############################## Helpers ##############################
#####################################################################
def init(b):
    global bot
    bot = b


async def registerServerWithDB(ctx):
    # instantiating a schedule and message collection entry if one doesn't exist
    msgObj = await getMessageObject(ctx)

    try:
        if not msgObj:
            await updateMessageObject(ctx, {'message': '', 'reactions': [], 'attachments': {'message_id': '', 'channel_id': ''}})
    except RuntimeError as e:
        raise Exception(e)


async def sendMessage(message, bot, content, channel=None, attachments=None):
    try:
        res = str(content)

        # content can't be empty
        if not content:
            raise ValueError('No message is set.')

        # specified channel
        if channel:
            c = bot.get_channel(channel)

            # non-existent channel
            if not c:
                raise RuntimeError(f"Could not find channel '{channel}' to send the message to.")

            return await c.send(content=res, files=attachments)

        return await message.channel.send(content=res, files=attachments)
    except RuntimeError as e:
        raise e
    except ValueError as e:
        raise e
    except Exception as e:
        print(e)


async def sendMessageByChannelID(content, channelID: int, attachments=None):
    try:
        res = str(content)

        # content can't be empty
        if not content:
            raise ValueError('No message is set.')

        channel = bot.get_channel(channelID)

        # non-existent channel
        if not channel:
            raise RuntimeError(f"Could not find channel '{channelID}' to send the message to.")

        return await channel.send(content=res, files=attachments)
    except RuntimeError as e:
        raise e
    except ValueError as e:
        raise e
    except Exception as e:
        print(e)


async def sendEmbeddedMessage(message, col, mainContent, fields=None, inline=False):
    embedVar = discord.Embed(
        title=mainContent['title'], description=mainContent['desc'], color=col)

    if fields:
        for field in fields:
            embedVar.add_field(name=field['name'],
                               value=field['value'], inline=inline)

    await message.channel.send(embed=embedVar)


async def getMessageObject(ctx):
    return pymongoManager.find_in_collection_by_id('messages', ctx.message.guild.id)


async def getScheduleByServerId(serverID):
    return pymongoManager.find_all_in_collection('schedules', {'server_id': serverID})


async def getPostById(postID: int):
    try:
        return pymongoManager.find_in_collection_by_id('schedules', int(postID))
    except RuntimeError as e:
        raise e


async def deletePostById(postID: int):
    try:
        pymongoManager.delete_by_id('schedules', int(postID))
    except RuntimeError as e:
        raise e


async def deleteServerPosts(serverID):
    try:
        pymongoManager.delete_all_by_query('schedules', {'server_id': serverID})
    except RuntimeError as e:
        raise e


async def updateMessageObject(ctx, data):
    try:
        pymongoManager.update_collection('messages', ctx.message.guild.id, data)
    except RuntimeError as e:
        raise e


async def handlePrint(ctx, bot, channel=None, postID=None):
    # determining which message object to use
    if not postID:
        messageObj = await getMessageObject(ctx)
    else:
        schedule = await getScheduleByServerId(ctx.message.guild.id)

        if int(postID) not in schedule.keys():
            raise ValueError(f"Could not find a post with post ID: {postID}")

        messageObj = schedule[int(postID)]

    # adding attachments
    attachments = []

    try:
        if messageObj['attachments']['message_id'] != '':
            msg = await ctx.fetch_message(messageObj['attachments']['message_id'])

            for f in msg.attachments:
                file = await f.to_file()
                attachments.append(file)
    except Exception as e:
        print(e)

    # sending the message
    try:
        msg = await sendMessage(ctx, bot, messageObj['message'], channel, attachments)
    except RuntimeError as e:
        raise e
    except ValueError as e:
        raise e

    # adding emojis
    for reaction in messageObj['reactions']:
        try:
            emoji = discord.utils.get(ctx.message.guild.emojis, name=reaction)  # set to a custom emoji by default

            if not emoji:  # standard emojis
                emoji = reaction

            await msg.add_reaction(emoji)
        except:
            print(f"Unknown emoji: {reaction}")


async def updateSchedule(id, data):
    try:
        pymongoManager.update_collection('schedules', id, data)
    except RuntimeError as e:
        raise e


async def validateChannel(channel):
    if not channel.isdigit():  # ensure that the provided value could be a channel
        raise ValueError("The channel must be a numerical value")


# dateData has 2 fields, date and time. date is in dd/mm/yyyy format and
# time is in hh:mm format
async def validateDate(dateData):
    date = dateData['date'].split('/')
    time = dateData['time'].split(':')

    if not (len(date) == 3 and date[0].isdigit() and date[1].isdigit() and date[2].isdigit() and len(date[0]) == 2 and len(date[1]) == 2 and len(date[2]) == 4):      # dd/mm/yyyy format check
        raise ValueError("The date was not provided in dd/mm/yyyy format.")
    elif not (len(time) == 2 and time[0].isdigit() and time[1].isdigit() and len(time[0]) == 2 and len(time[1]) == 2):  # hh:mm format check
        raise ValueError("The time was not provided in hh:mm format.")


async def sendPost(post):
    server = await bot.fetch_guild(int(post['server_id']))

    # adding attachments
    attachments = []

    try:
        if post['attachments']['message_id'] != '' and post['attachments']['channel_id'] != '':
            channel = await bot.fetch_channel(int(post['attachments']['channel_id']))
            msg = await channel.fetch_message(int(post['attachments']['message_id']))

            for f in msg.attachments:
                file = await f.to_file()
                attachments.append(file)
    except Exception as e:
        print(e)

    # sending the message
    try:
        msg = await sendMessageByChannelID(post['message'], int(post['channel']), attachments)
    except RuntimeError as e:
        raise e
    except ValueError as e:
        raise e

    # adding emojis
    if server:
        for reaction in post['reactions']:
            try:
                emoji = discord.utils.get(server.emojis, name=reaction)  # set to a custom emoji by default

                if not emoji:  # standard emojis
                    emoji = reaction

                await msg.add_reaction(emoji)
            except:
                print(f"Unknown emoji: {reaction}")


def getSecondsFromNextMinute():
    now = datetime.now()
    nextMinute = datetime(now.year, now.month, now.day, now.hour, now.minute+1, 0, 0)

    return (nextMinute-now).seconds


@tasks.loop(seconds=0)
async def manageScheduleLoop():
    delay = getSecondsFromNextMinute()

    if delay == 0:
        return

    await asyncio.sleep(delay)

    # determining if there are any posts to be posted for the current minute
    date = datetime.now().astimezone(timezone.utc)

    posts = pymongoManager.get_posts_in_date_range(date + timedelta(minutes=-2), date)

    # posting the posts if there are any
    for post in posts:
        try:
            await sendPost(post)
            await deletePostById(post['_id'])
        except Exception as e:
            print(e)


@manageScheduleLoop.before_loop
async def beforeLoop():
    await bot.wait_until_ready()
    print("Scheduling loop started")

#####################################################################
############################# Handlers ##############################
#####################################################################
async def handleReady():
    print("Bot connected")


async def handleAdd(ctx, rawArgs):
    dateFormat = '%d/%m/%YT%H:%M:%S%z'

    # argument validation
    args = rawArgs.strip().split(' ')

    try:
        if len(args) != 3:
            raise ValueError("Please provide exactly 3 arguments to the 'add' command.")

        await validateChannel(args[0])
        await validateDate({'date': args[1], 'time': args[2]})
    except ValueError as e:
        raise e

    # formatting the data
    channel = int(args[0])
    dateObj = datetime.strptime(args[1] + 'T' + args[2] + ':00+00:00', dateFormat)

    # getting stored message
    msgObj = await getMessageObject(ctx)

    # no message was set
    if msgObj['message'] == '':
        raise ValueError('No message was set! This command was ignored.')

    # setting the postID to the message id of the message that called the 'add' command
    postID = ctx.message.id

    # db updates
    try:
        scheduleData = {'server_id': ctx.message.guild.id, 'channel': channel, 'message': msgObj['message'],
                        'reactions': msgObj['reactions'], 'attachments': msgObj['attachments'], 'time': dateObj}
    except Exception as e:
        print(e)

    try:
        await updateSchedule(postID, scheduleData)  # schedule the current message
    except RuntimeError as e:
        print(e)
        raise RuntimeError("Could not add the message to the schedule.")

    try:
        await updateMessageObject(ctx, {'message': '', 'reactions': [], 'attachments': {'message_id': '', 'channel_id': ''}})  # reset the current message
    except:
        print(e)
        raise RuntimeError("Schedule updated, but the message was not reset.")

    # informing the user
    await sendEmbeddedMessage(ctx, 0x00FF00, {'title': "Success",
                                              'desc': f"Message added to post schedule!\n\n**Post ID**: {postID}"})

async def handleRemove(ctx, msg):
    postID = msg.strip().split(' ')[0]

    if not postID.isdigit():
        raise TypeError("Invalid post ID: {postID}. Post IDs may only contain numbers.")

    post = await getPostById(int(postID))

    # no scheduled post corresponds with the provided one
    if not post:
        raise ValueError(f"There is no scheduled post with the corresponding post ID: {postID}")

    # deleting the msg
    try:
       await deletePostById(int(postID))
    except RuntimeError as e:
        print(e)
        raise RuntimeError(f"Could not delete the post with ID: {postID}. The command will be ignored.")

    await sendEmbeddedMessage(ctx, 0x00FF00, {'title': "Success",
                                              'desc': f"Post with ID {postID} was removed from the post schedule!"})


async def handleSet(ctx, msg):
    msgObj = await getMessageObject(ctx)
    msgObj['message'] = msg
    msgObj['attachments'] = {'message_id': ctx.message.id, 'channel_id': ctx.message.channel.id}

    await updateMessageObject(ctx, msgObj)

    # no text was provided
    if msg == '':
        await sendEmbeddedMessage(ctx, 0x00FF00, {'title': "Success", 'desc': 'The message was cleared!'})
        return

    await sendEmbeddedMessage(ctx, 0x00FF00, {'title': "Success", 'desc': 'The message has been set!'})


async def handleSetReaction(ctx, msg):
    emojis = msg.strip().split(' ')

    msgObj = await getMessageObject(ctx)

    msgObj['reactions'] = emojis

    await updateMessageObject(ctx, msgObj)

    # no emojis specified
    if len(emojis) == 1 and emojis[0] == '':
        await sendEmbeddedMessage(ctx, 0x00FF00, {'title': "Success", 'desc': f"Reactions were cleared!"})
        return

    await sendEmbeddedMessage(ctx, 0x00FF00, {'title': "Success", 'desc': f"Reaction(s) {msg} added to message!"})


async def handleReset(ctx):
    try:
        await updateMessageObject(ctx, {'message': '', 'reactions': [], 'attachments': {'message_id': '', 'channel_id': ''}})
    except RuntimeError as e:
        print(e)
        raise RuntimeError(f"Could not reset the message. The command will be ignored.")

    await sendEmbeddedMessage(ctx, 0x00FF00, {'title': "Success", 'desc': 'The message has been reset!'})

async def handleClear(ctx):
    try:
        await deleteServerPosts(ctx.message.guild.id)
    except RuntimeError as e:
        print(e)
        raise RuntimeError(f"Could not delete all scheduled posts for this server. This command will be ignored.")

    await sendEmbeddedMessage(ctx, 0x00FF00, {'title': "Success", 'desc': 'The post schedule was cleared!'})

async def handlePreview(ctx, bot, rawArgs):
    # getting the type of print operation
    args = rawArgs.strip().split(' ')

    postType = args[0]

    if len(args) != 1 or (postType != 'current' and not postType.isdigit()):
        raise ValueError('The provided arguments are invalid. Command will be ignored.')

    # determining which message to print
    try:
        if postType == 'current':
            await handlePrint(ctx, bot)
        else:
            await handlePrint(ctx, bot, postID=postType)
    except RuntimeError as e:
        raise e
    except ValueError as e:
        raise e


async def handleList(ctx):
    schedule = await getScheduleByServerId(ctx.message.guild.id)

    # no scheduled posts
    if not schedule or len(schedule) == 0:
        await sendEmbeddedMessage(ctx, 0xFFFF00, {'title': "Warning", 'desc': f"You don't have any scheduled posts!"})
        return

    # returning a list of the schedule
    msg = ""
    count = 1

    msgList = []

    for postID in schedule.keys():
        msg += f"**#{count}**\n" \
                   f"**Post ID**: {postID}\n" \
                   f"**Post Time**: {schedule[postID]['time']}\n" \
                   f"**Preview**: {schedule[postID]['message'] if len(schedule[postID]['message']) < 50 else schedule[postID]['message'][0:47] + '...'}\n\n"

        if len(msg) > 1500:
            msgList.append(msg)
            msg = ''

        count += 1

    msgList.append(msg)

    for message in msgList:
        await sendEmbeddedMessage(ctx, 0x00FF00, {'title': "Posts", 'desc': message})


async def handleHelp(ctx):
    helpDesc = '''The Message Scheduler is used to schedule your posts based on the message that you set via the 'set' command (and any modifications made with appropriate commands. E.g. 'reaction'). If you don't like your message, you can override it with another message via the 'set' command, or if you have made other modifications to the message (e.g. via 'reaction'), you can use the 'reset' command to reset the message entirely.
Once you are happy with the message, you can schedule it via the 'add' command. If you want to delete the message after it has been scheduled, simply use the 'remove' command with the ID that you were provided when the messaged was scheduled.
    
The commands are as follows:'''

    addMsg = '''Adds the created message to the schedule. Note that a message must be created before it can be added to the schedule, and times are specified in UTC.
    
BTW:
UTC Time = EST Time + 4 hours
UTC Time = EDT Time + 5 hours
    
Format: !ms add <channel> <post date> <post time>
    
E.g. !ms add 1143322446909407323 30/01/2023 23:59
This would post the message on January 30, 2023 at 11:59 PM to the channel with ID 1143322446909407323'''

    removeMsg = '''Removes a message from the schedule based on a post ID.
    
Format: !ms remove <message post id>
    
E.g. !ms remove 123'''

    setMsg = '''Sets the message to be scheduled.
    
Format: !ms set <message>
    
E.g. !ms set This is an announcement'''

    reactionMsg = '''Sets the reactions for the message.
    
Format: !ms reaction [<emoji>]
    
E.g. !ms reaction 😄 😢 🥯'''

    resetMsg = '''Resets the message and all modifications made to it
    
Format: !ms reset
    
E.g. !ms reset'''

    clearMsg = '''Un-schedules all previously scheduled messages
    
Format: !ms clearSchedule
    
E.g. !ms clearSchedule'''

    previewMsg = '''Displays either the message that is currently being worked on or a particular scheduled post.
    
Format: !ms preview <current|post ID>
    
E.g. !ms preview current'''

    listMsg = '''Lists all the currently scheduled messages, with their postID, post time, and a preview of their content.
    
Format: !ms list
    
E.g. !ms list'''

    fields = [
        {'name': 'add', 'value': addMsg},
        {'name': 'remove', 'value': removeMsg},
        {'name': 'set', 'value': setMsg},
        {'name': 'reaction', 'value': reactionMsg},
        {'name': 'reset', 'value': resetMsg},
        {'name': 'clearSchedule', 'value': clearMsg},
        {'name': 'preview', 'value': previewMsg},
        {'name': 'list', 'value': listMsg}
    ]

    await sendEmbeddedMessage(ctx, 0x7e42f5, {'title': "Message Scheduler Commands", 'desc': helpDesc}, fields)


async def handleSchedule(ctx, bot, cmd, args):
    # creating a schedule and message object for new servers
    await registerServerWithDB(ctx)

    # interpreting commands
    try:
        if cmd == 'add':
            await handleAdd(ctx, args)
        elif cmd == 'remove':
            await handleRemove(ctx, args)
        elif cmd == 'set':
            await handleSet(ctx, args)
        elif cmd == 'reaction':
            await handleSetReaction(ctx, args)
        elif cmd == 'reset':
            await handleReset(ctx)
        elif cmd == 'clearSchedule':
            await handleClear(ctx)
        elif cmd == 'preview':
            await handlePreview(ctx, bot, args)
        elif cmd == 'list':
            await handleList(ctx)
        elif cmd == 'help':
            await handleHelp(ctx)
        else:
            await sendEmbeddedMessage(ctx, 0xFFFF00, {'title': 'Warning', 'desc': "Unrecognized command. Type '!ms help' for the list of commands!"})
    except ValueError as e:  # this only throws if the user provided invalid arguments
        await sendEmbeddedMessage(ctx, 0xFF0000, {'title': 'ERROR', 'desc': e})
    except TypeError as e:
        await sendEmbeddedMessage(ctx, 0xFF0000, {'title': 'ERROR', 'desc': e})
    except RuntimeError as e:
        await sendEmbeddedMessage(ctx, 0xFF0000, {'title': 'ERROR', 'desc': e})
    except Exception:
        await sendEmbeddedMessage(ctx, 0xFF0000, {'title': 'ERROR', 'desc': 'An error occurred. Command will be ignored.'})
