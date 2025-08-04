import bot
from dotenv import load_dotenv
from managers.pymongo_manager import *

try:
    load_dotenv()
    PymongoManager.connect()
    bot.run_discord_bot()
except Exception as e:
    raise e
