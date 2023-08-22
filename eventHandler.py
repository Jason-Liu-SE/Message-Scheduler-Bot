import pymongoManager

client = None

#####################################################################
############################## Helpers ##############################
#####################################################################
def init(c):
    global client
    client = c

def updateChannelData(message, data):
  pymongoManager.update_collection('active_channels', message.guild.id, {'server_name': str(message.guild.name), 'channel_data': data})

def getLastChannelUser(message):
  rawData = pymongoManager.find_in_collection('active_channels', message.guild.id)

  if rawData:
    return rawData['channel_data']

  return None

async def sendMessage(message, uMessage):
  try:
    res = str(uMessage)
    await message.channel.send(res)
  except Exception as e:
    print(e)

#####################################################################
############################# Handlers ##############################
#####################################################################
async def handleReady():
    print("Bot connected")

async def handleScheduleAdd(ctx, bot):
    print(ctx)
    print(bot)
