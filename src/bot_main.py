import bot
from dotenv import load_dotenv
import helpers.pymongoManager as pymongoManager

try:
    load_dotenv()
    pymongoManager.connect()
    bot.runDiscordBot()
except Exception as e:
    raise e
