from datetime import datetime


class Logger:
    __colours = {
        "BLUE": "\033[94m",
        "YELLOW": "\033[93m",
        "RED": "\033[91m",
        "DARKGRAY": "\033[90m",
        "ENDC": "\033[0m",
        "BOLD": "\033[1m",
    }

    @staticmethod
    def __get_date():
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def info(message):
        print(
            f"{Logger.__colours["BOLD"]}{Logger.__colours["DARKGRAY"]}{Logger.__get_date()} "
            + f"{Logger.__colours["BLUE"]}INFO\t{Logger.__colours["ENDC"]} {message}"
        )

    @staticmethod
    def warn(message):
        print(
            f"{Logger.__colours["BOLD"]}{Logger.__colours["DARKGRAY"]}{Logger.__get_date()} "
            + f"{Logger.__colours["YELLOW"]}WARNING\t{message}{Logger.__colours["ENDC"]}"
        )

    @staticmethod
    def error(message):
        print(
            f"{Logger.__colours["BOLD"]}{Logger.__colours["DARKGRAY"]}{Logger.__get_date()} "
            + f"{Logger.__colours["RED"]}ERROR\t{message}{Logger.__colours["ENDC"]}"
        )
