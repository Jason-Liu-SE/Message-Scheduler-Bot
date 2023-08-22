import bot
from dotenv import load_dotenv
import pymongoManager

if __name__ == '__main__':
    load_dotenv()
    pymongoManager.connect()
    bot.runDiscordBot()