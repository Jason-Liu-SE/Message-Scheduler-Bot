import bot
from dotenv import load_dotenv
import pymongoManager
from keep_alive import keep_alive

if __name__ == '__main__':
    load_dotenv()
    keep_alive()
    pymongoManager.connect()
    bot.runDiscordBot()