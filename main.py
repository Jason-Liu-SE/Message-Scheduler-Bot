import subprocess
import time

if __name__ == '__main__':
    while True:
        try:
            print("Starting message scheduler bot subprocess")
            bot_process = subprocess.Popen(["python", "bot_main.py"])
            bot_process.wait()
            print("Exiting message scheduler bot subprocess")
            time.sleep(5)
        except Exception as e:
            print(f"FATAL ERROR: Bot crashed with error: {e}")
            time.sleep(5)
