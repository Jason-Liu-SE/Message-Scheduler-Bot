import subprocess
import time

from helpers.logger import Logger
from rich.traceback import install


def delay_restart():
    Logger.info("Restarting in 1 minute")
    time.sleep(60)


if __name__ == "__main__":
    while True:
        try:
            install()
            Logger.info("Starting message scheduler bot subprocess")
            # Use bot_process = subprocess.Popen(["python", "./src/bot_main.py"]) for Koyeb deployment
            # and bot_process = subprocess.Popen(["python", "./bot_main.py"]) otherwise
            bot_process = subprocess.Popen(["python", "./src/bot_main.py"])
            bot_process.wait()
            Logger.info("Exiting message scheduler bot subprocess")
        except Exception as e:
            Logger.error(f"Bot crashed with error: {e}")
        delay_restart()
