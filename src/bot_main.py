import bot
from dotenv import load_dotenv
from managers.pymongo_manager import *

load_dotenv()
PymongoManager.connect()
bot.run_discord_bot()
