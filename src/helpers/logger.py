class Logger:
    colours = {
        "WARNING": "\033[93m",
        "ERROR": "\033[91m",
        "ENDC": "\033[0m",
    }

    @staticmethod
    def info(message):
        print(f"[INFO]: {message}")

    @staticmethod
    def warn(message):
        print(
            f"{Logger.colours["WARNING"]}[WARNING]: {message}{Logger.colours["ENDC"]}"
        )

    @staticmethod
    def error(message):
        print(f"{Logger.colours["ERROR"]}[ERROR]: {message}{Logger.colours["ENDC"]}")
