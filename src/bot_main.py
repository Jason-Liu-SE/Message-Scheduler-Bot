import bot
from dotenv import load_dotenv
import helpers.pymongo_manager as pymongo_manager

try:
    load_dotenv()
    pymongo_manager.connect()
    bot.runDiscordBot()
except Exception as e:
    raise e
