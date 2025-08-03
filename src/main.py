import subprocess
import time

from helpers.logger import Logger


def delay_restart():
    Logger.info("Restarting in 1 minute")
    time.sleep(60)


if __name__ == "__main__":
    while True:
        try:
            Logger.info("Starting message scheduler bot subprocess")
            bot_process = subprocess.Popen(["python", "./src/bot_main.py"])
            bot_process.wait()
            Logger.info("Exiting message scheduler bot subprocess")
        except Exception as e:
            Logger.error(f"Bot crashed with error: {e}")
        delay_restart()
