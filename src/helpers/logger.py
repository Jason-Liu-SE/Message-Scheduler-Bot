from datetime import datetime
from rich.console import Console
from rich.traceback import Traceback


class Logger:
    __colours = {
        "BLUE": "\033[94m",
        "YELLOW": "\033[93m",
        "RED": "\033[91m",
        "DARKGRAY": "\033[90m",
        "ENDC": "\033[0m",
        "BOLD": "\033[1m",
    }

    __console = Console()

    @staticmethod
    def __get_date():
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def info(message: str) -> None:
        print(
            f"{Logger.__colours["BOLD"]}{Logger.__colours["DARKGRAY"]}{Logger.__get_date()} "
            + f"{Logger.__colours["BLUE"]}INFO\t{Logger.__colours["ENDC"]}{message}"
        )

    @staticmethod
    def warn(message: str) -> None:
        print(
            f"{Logger.__colours["BOLD"]}{Logger.__colours["DARKGRAY"]}{Logger.__get_date()} "
            + f"{Logger.__colours["YELLOW"]}WARNING{Logger.__colours["ENDC"]}\t"
            + f"{Logger.__colours["YELLOW"]}{message}{Logger.__colours["ENDC"]}"
        )

    @staticmethod
    def error(message: str) -> None:
        print(
            f"{Logger.__colours["BOLD"]}{Logger.__colours["DARKGRAY"]}{Logger.__get_date()} "
            + f"{Logger.__colours["RED"]}ERROR{Logger.__colours["ENDC"]}\t"
            + f"{Logger.__colours["RED"]}{message}{Logger.__colours["ENDC"]}"
        )

    @staticmethod
    def traceback(error: error) -> None:
        Logger.__console.print(
            Traceback.from_exception(type(error), error, error.__traceback__)
        )

    @staticmethod
    def exception(error: error) -> None:
        Logger.error(error)
        Logger.traceback(error)
