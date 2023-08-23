import pymongoManager
import discord

client = None

#####################################################################
############################## Helpers ##############################
#####################################################################
def init(c):
    global client
    client = c


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


async def sendEmbeddedMessage(message, col, mainContent, fields, inline=False):
    embedVar = discord.Embed(
        title=mainContent['title'], description=mainContent['desc'], color=col)

    for field in fields:
        embedVar.add_field(name=field['name'],
                           value=field['value'], inline=inline)

    await message.channel.send(embed=embedVar)


async def getMessageObject(ctx):
    return pymongoManager.find_in_collection('messages', ctx.message.guild.id)


async def updateMessageObject(ctx, data):
    pymongoManager.update_collection('messages', ctx.message.guild.id, data)


async def handlePrint(ctx, bot, channel=None):
    # getting the message
    messageObj = await getMessageObject(ctx)

    if not messageObj:
        raise RuntimeError(f"Could not find an DB entry for server. Name:'{ctx.message.guild.name}'. ID: '{ctx.message.guild.id}'")

    # adding attachments
    attachments = []

    for filename in messageObj['attachments']:
        with open(filename, 'rb') as f:  # discord file objects must be opened in binary and read mode
            attachments.append(discord.File(f))

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

#####################################################################
############################# Handlers ##############################
#####################################################################
async def handleReady():
    print("Bot connected")


async def handleAdd(ctx, bot, msg):
    id = 127391823812793
    await sendEmbeddedMessage(ctx, 0x00FF00, {'title': "Success", 'desc': f"Message added to post schedule!\n\n**Post ID**: {id}."}, [])


async def handleRemove(ctx, bot, msg):
    id = 127391823812793
    await sendEmbeddedMessage(ctx, 0x00FF00, {'title': "Success", 'desc': f"Post with ID {id} was removed from the post schedule!"}, [])


async def handleSet(ctx, msg):
    msgObj = await getMessageObject(ctx)

    msgObj['message'] = msg

    await updateMessageObject(ctx, msgObj)

    # no text was provided
    if msg == '':
        await sendEmbeddedMessage(ctx, 0x00FF00, {'title': "Success", 'desc': 'The message was cleared!'}, [])
        return

    await sendEmbeddedMessage(ctx, 0x00FF00, {'title': "Success", 'desc': 'The message has been set!'}, [])


async def handleSetReaction(ctx, msg):
    emojis = msg.strip().split(' ')

    msgObj = await getMessageObject(ctx)

    msgObj['reactions'] = emojis

    await updateMessageObject(ctx, msgObj)

    # no emojis specified
    if len(emojis) == 1 and emojis[0] == '':
        await sendEmbeddedMessage(ctx, 0x00FF00, {'title': "Success", 'desc': f"Reactions were cleared!"}, [])
        return

    await sendEmbeddedMessage(ctx, 0x00FF00, {'title': "Success", 'desc': f"Reaction(s) {msg} added to message!"}, [])


async def handleReset(ctx):
    await updateMessageObject(ctx, {'message': '', 'reactions': [], 'attachments': []})
    await sendEmbeddedMessage(ctx, 0x00FF00, {'title': "Success", 'desc': 'The message has been reset!'}, [])


async def handleClear(ctx):
    await sendEmbeddedMessage(ctx, 0x00FF00, {'title': "Success", 'desc': 'The post schedule was cleared!'}, [])


async def handleView(ctx, bot, rawArgs):
    # getting the type of print operation
    args = rawArgs.strip().split(' ')

    channel = args[0]

    if len(args) != 1 or (channel != 'current' and not channel.isdigit()):
        raise ValueError('The provided arguments are invalid. Command will be ignored.')

    # determining which message to print
    try:
        if channel == 'current':
            await handlePrint(ctx, bot)
        else:
            await handlePrint(ctx, bot, int(channel))
    except RuntimeError as e:
        raise e
    except ValueError as e:
        raise e


async def handleHelp(ctx):
    helpDesc = '''The Message Scheduler is used to schedule your posts based on the message that you set via the 'set' command (and any modifications made with appropriate commands. E.g. 'reaction').

                          If you don't like your message, you can override it with another message via the 'set' command, or if you have made other modifications to the message
                          (e.g. via 'reaction'), you can use the 'reset' command to reset the message entirely.

                          Once you are happy with the message, you can schedule it via the 'add' command. If you want to delete the message after it has been scheduled, simply use
                          the 'remove' command with the ID that you were provided when the messaged was scheduled.

                          The commands are as follows:'''

    addMsg = '''Adds the proceeding message to the schedule in the provided channel (by ID).
                        Format: !ms add <channel> <post date> <post time>

                        E.g. !ms add 1143322446909407323 30/01/2023 23/59
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
                          Format: !ms clear

                          E.g. !ms clear'''

    viewMsg = '''Displays either the message that is currently being worked on or a particular scheduled post.
                              Format: !ms view <current|post ID>

                              E.g. !ms view current'''

    fields = [
        {'name': 'add', 'value': addMsg},
        {'name': 'remove', 'value': removeMsg},
        {'name': 'set', 'value': setMsg},
        {'name': 'reaction', 'value': reactionMsg},
        {'name': 'reset', 'value': resetMsg},
        {'name': 'clear', 'value': clearMsg},
        {'name': 'view', 'value': viewMsg}
    ]

    await sendEmbeddedMessage(ctx, 0x7e42f5, {'title': "Message Scheduler Commands", 'desc': helpDesc}, fields)


async def handleSchedule(ctx, bot, cmd, args):
    try:
        if cmd == 'add':
            await handleAdd(ctx, bot, args)
        elif cmd == 'remove':
            await handleRemove(ctx, bot, args)
        elif cmd == 'set':
            await handleSet(ctx, args)
        elif cmd == 'reaction':
            await handleSetReaction(ctx, args)
        elif cmd == 'reset':
            await handleReset(ctx)
        elif cmd == 'clear':
            await handleClear(ctx)
        elif cmd == 'view':
            await handleView(ctx, bot, args)
        elif cmd == 'help':
            await handleHelp(ctx)
        else:
            await sendEmbeddedMessage(ctx, 0xFFFF00, {'title': 'Warning', 'desc': "Unrecognized command. Type '!ms help' for the list of commands!"}, [])
    except ValueError as e:  # this only throws if the user provided invalid arguments
        await sendEmbeddedMessage(ctx, 0xFF0000, {'title': 'ERROR', 'desc': e}, [])
    except RuntimeError as e:
        await sendEmbeddedMessage(ctx, 0xFF0000, {'title': 'ERROR', 'desc': e}, [])
    except Exception as e:
        await sendEmbeddedMessage(ctx, 0xFF0000, {'title': 'ERROR', 'desc': 'An error occurred. Command will be ignored.'}, [])
