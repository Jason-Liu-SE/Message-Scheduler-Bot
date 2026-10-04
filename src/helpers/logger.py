from datetime import datetime
from rich.console import Console
from rich.traceback import Traceback


class Logger:
    _colours = {
        "BLUE": "\033[94m",
        "YELLOW": "\033[93m",
        "RED": "\033[91m",
        "DARKGRAY": "\033[90m",
        "ENDC": "\033[0m",
        "BOLD": "\033[1m",
    }

    _console = Console()

    @staticmethod
    def __get_date():
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def info(message: str) -> None:
        print(
            f"{Logger._colours["BOLD"]}{Logger._colours["DARKGRAY"]}{Logger.__get_date()} "
            + f"{Logger._colours["BLUE"]}INFO\t{Logger._colours["ENDC"]}{message}"
        )

    @staticmethod
    def warn(message: str) -> None:
        print(
            f"{Logger._colours["BOLD"]}{Logger._colours["DARKGRAY"]}{Logger.__get_date()} "
            + f"{Logger._colours["YELLOW"]}WARNING{Logger._colours["ENDC"]}\t"
            + f"{Logger._colours["YELLOW"]}{message}{Logger._colours["ENDC"]}"
        )

    @staticmethod
    def error(message: str) -> None:
        print(
            f"{Logger._colours["BOLD"]}{Logger._colours["DARKGRAY"]}{Logger.__get_date()} "
            + f"{Logger._colours["RED"]}ERROR{Logger._colours["ENDC"]}\t"
            + f"{Logger._colours["RED"]}{message}{Logger._colours["ENDC"]}"
        )

    @staticmethod
    def traceback(error: error) -> None:
        Logger._console.print(
            Traceback.from_exception(type(error), error, error.__traceback__)
        )

    @staticmethod
    def exception(error: error) -> None:
        Logger.error(error)
        Logger.traceback(error)
