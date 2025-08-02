import bot
from dotenv import load_dotenv
import pymongoManager
from keep_alive import keep_alive

try:
    load_dotenv()
    pymongoManager.connect()
    bot.runDiscordBot()
except Exception as e:
    raise e