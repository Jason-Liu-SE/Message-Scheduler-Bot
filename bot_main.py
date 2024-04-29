import bot
from dotenv import load_dotenv
import pymongoManager
from keep_alive import keep_alive

try:
    load_dotenv()
    # keep_alive()
    pymongoManager.connect()
    bot.runDiscordBot()
except Exception as e:
    raise e