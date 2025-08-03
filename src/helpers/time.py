from datetime import datetime, timedelta, timezone
from helpers.logger import Logger


# dateData has 2 fields, date and time. date is in dd/mm/yyyy format and
# time is in hh:mm format
async def validate_date(date_data):
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


async def validate_time(date_obj):
    if date_obj <= datetime.now().astimezone(timezone.utc):
        raise ValueError(f"The time must be in the future.")


def get_seconds_from_next_minute():
    try:
        now = datetime.now()
        next_minute = datetime(
            now.year, now.month, now.day, now.hour, now.minute, 0, 0
        ) + timedelta(minutes=1)

        return (next_minute - now).seconds
    except Exception as e:
        Logger.error(e)
        return 0
