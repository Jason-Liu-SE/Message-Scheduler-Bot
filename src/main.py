import subprocess
import time


def delay_restart():
    print("Restarting in 1 minute")
    time.sleep(60)


if __name__ == "__main__":
    while True:
        try:
            print("Starting message scheduler bot subprocess")
            bot_process = subprocess.Popen(["python", "./src/bot_main.py"])
            bot_process.wait()
            print("Exiting message scheduler bot subprocess")
        except Exception as e:
            print(f"FATAL ERROR: Bot crashed with error: {e}")
        delay_restart()
