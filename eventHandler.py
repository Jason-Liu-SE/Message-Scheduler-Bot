import pymongoManager
import discord

client = None

#####################################################################
############################## Helpers ##############################
#####################################################################
def init(c):
    global client
    client = c

async def sendMessage(message, content):
  try:
    res = str(content)
    await message.channel.send(res)
  except Exception as e:
    print(e)

async def sendEmbeddedMessage(message, col, mainContent, fields):
    embedVar = discord.Embed(title=mainContent['title'], description=mainContent['desc'], color=col)

    for field in fields:
        embedVar.add_field(name=field['name'], value=field['value'], inline=False)

    await message.channel.send(embed=embedVar)

#####################################################################
############################# Handlers ##############################
#####################################################################
async def handleReady():
    print("Bot connected")

async def handleAdd(ctx, bot, msg):
    print("added")

async def handleRemove(ctx, bot, msg):
    print("removed")

async def handleSet(ctx, bot, msg):
    print("set")

async def handleAddReaction(ctx, bot, msg):
    print("reaction added")

async def handleReset(ctx, bot, args):
    print("message reset")

async def handleClear(ctx, bot, args):
    print("schedule cleared")

async def handleSchedule(ctx, bot, cmd, *args):
    for arg in args:
      print(arg)

    try:
        if cmd == 'add':
            await handleAdd(ctx, bot, args)
        elif cmd == 'remove':
            await handleRemove(ctx, bot, args)
        elif cmd == 'set':
            await handleSet(ctx, bot, args)
        elif cmd == 'reaction':
            await handleAddReaction(ctx, bot, args)
        elif cmd == 'reset':
            await handleReset(ctx, bot, args)
        elif cmd == 'clear':
            await handleClear(ctx, bot, args)
        else:
            await sendEmbeddedMessage(ctx, 0xFF0000, {'title': 'ERROR', 'desc': 'Unrecognized command. Try !scheduleHelp for the list of commands.'}, [])
    except Exception as e:  # this only throws if the user provided invalid arguments
        await sendEmbeddedMessage(ctx, 0xFF0000, {'title': 'ERROR', 'desc': 'The provided arguments are invalid. Command will be ignored.'}, [])

async def handleHelp(ctx):
    helpDesc = '''The Message Scheduler works based on the message that you set via the 'set' command (and any modifications made with appropriate commands. E.g. 'reaction').

                      If you don't like your message, you can override it with another message via the 'set' command, or if you have made other modifications to the message
                      (e.g. via 'reaction'), you can use the 'reset' command to reset the message entirely.

                      Once you are happy with the message, you can schedule it via the 'add' command. If you want to delete the message after it has been scheduled, simply use
                      the 'remove' command with the ID that you were provided when the messaged was scheduled.

                      The commands are as follows:'''

    addMsg = '''Adds the proceeding message to the schedule in the provided channel (by ID).
                    Format: !schedule add <channel> <post date> <post time>

                    E.g. !schedule add 1143322446909407323 30/01/2023 23/59
                    This would post the message on January 30, 2023 at 11:59 PM to the channel with id 1143322446909407323'''

    removeMsg = '''Removes the proceeding message from the schedule based on the schedule id.
                       Format: !schedule remove <message schedule id>

                       E.g. !schedule remove 123'''

    setMsg = '''Sets the message to be scheduled.
                    Format: !schedule set <message>

                    E.g. !schedule set This is an announcement'''

    reactionMsg = '''Adds a reaction to the message.
                         Format: !schedule reaction <reaction name>

                         E.g. !schedule reaction happy'''

    resetMsg = '''Resets the message and all modifications made to it
                      Format: !schedule reset

                      E.g. !schedule reset'''

    clearMsg = '''Un-schedules all previously scheduled messages
                      Format: !schedule clear

                      E.g. !schedule clear'''

    fields = [
        {'name': 'add', 'value': addMsg},
        {'name': 'remove', 'value': removeMsg},
        {'name': 'set', 'value': setMsg},
        {'name': 'reaction', 'value': reactionMsg},
        {'name': 'reset', 'value': resetMsg},
        {'name': 'clear', 'value': clearMsg}
    ]

    await sendEmbeddedMessage(ctx, 0x00ff00, {'title': "Message Scheduler Commands", 'desc': helpDesc}, fields)