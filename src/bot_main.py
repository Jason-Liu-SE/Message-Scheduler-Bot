import bot
from dotenv import load_dotenv
from helpers import keep_alive
from managers.pymongo_manager import *

load_dotenv()
keep_alive()
PymongoManager.connect()
bot.run_discord_bot()
