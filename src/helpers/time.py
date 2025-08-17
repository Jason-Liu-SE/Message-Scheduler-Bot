from datetime import UTC, datetime, timedelta, timezone
from helpers.logger import Logger
import pytz


# dateData has 2 fields, date and time. date is in dd/mm/yyyy format and
# time is in hh:mm format
async def validate_date(date_data: str) -> None:
    date = date_data["date"].split("/")
    time = date_data["time"].split(":")

    # dd/mm/yyyy format check
    if not (
        len(date) == 3
        and date[0].isdigit()
        and date[1].isdigit()
        and date[2].isdigit()
        and len(date[0]) == 2
        and len(date[1]) == 2
        and len(date[2]) == 4
    ):
        raise ValueError("The date was not provided in dd/mm/yyyy format.")
    # hh:mm format check
    elif not (
        len(time) == 2
        and time[0].isdigit()
        and time[1].isdigit()
        and len(time[0]) == 2
        and len(time[1]) == 2
    ):
        raise ValueError("The time was not provided in hh:mm format.")


async def validate_time(date_obj: datetime) -> None:
    if date_obj <= datetime.now().astimezone(timezone.utc):
        raise ValueError(f"The time must be in the future.")


def get_seconds_from_next_minute() -> int:
    try:
        now = datetime.now()
        next_minute = datetime(
            now.year, now.month, now.day, now.hour, now.minute, 0, 0
        ) + timedelta(minutes=1)

        return (next_minute - now).seconds
    except Exception as e:
        Logger.exception(e)
        return 0


# Converts dt to utc, assuming that it has a timezone of interpreted_timezone
# Note: this only works for dt that don't already have a timezone. E.g.
# new datetime objects that have been manually constructed.
def convert_to_utc(dt: datetime, interpreted_timezone: str) -> datetime:
    tz = pytz.timezone(interpreted_timezone)
    dt_localized = dt.astimezone(tz)

    utc_offset_s = 86400 - dt_localized.utcoffset().seconds

    return dt + timedelta(seconds=utc_offset_s)


# Converts a dt (with an existing timezone) to the specified timezone
def convert_to_timezone(dt: datetime, timezone: str = "Canada/Eastern") -> datetime:
    tz = pytz.timezone(timezone)
    return dt.astimezone(tz)


def format_date_time(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def replace_tz(dt: datetime, tz_name: str) -> datetime:
    tz = pytz.timezone(tz_name)
    return tz.localize(dt)
