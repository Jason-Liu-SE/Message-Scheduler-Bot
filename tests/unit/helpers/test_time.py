from datetime import datetime, timedelta, timezone

import pytest
import pytz

from helpers.time import (
    convert_to_timezone,
    format_date_time,
    get_seconds_from_next_minute,
    replace_tz,
    validate_date,
    validate_time,
)


@pytest.mark.unit
class TestValidateDate:
    async def test_accepts_dd_mm_yyyy_and_hh_mm(self):
        await validate_date({"date": "03/10/2026", "time": "09:30"})

    async def test_rejects_wrong_date_format(self):
        with pytest.raises(ValueError, match="dd/mm/yyyy"):
            await validate_date({"date": "2026-10-03", "time": "09:30"})

    async def test_rejects_wrong_time_format(self):
        with pytest.raises(ValueError, match="hh:mm"):
            await validate_date({"date": "03/10/2026", "time": "9:30"})


@pytest.mark.unit
class TestValidateTime:
    async def test_rejects_past_datetime(self):
        past = datetime.now(timezone.utc) - timedelta(minutes=1)
        with pytest.raises(ValueError, match="future"):
            await validate_time(past)

    async def test_accepts_future_datetime(self):
        future = datetime.now(timezone.utc) + timedelta(days=1)
        await validate_time(future)


@pytest.mark.unit
class TestTimeFormatting:
    def test_seconds_until_next_minute_is_in_range(self):
        remaining = get_seconds_from_next_minute()
        assert 0 <= remaining <= 60

    def test_format_date_time(self):
        dt = datetime(2026, 10, 3, 9, 5, 7)
        assert format_date_time(dt) == "2026-10-03 09:05:07"

    def test_replace_tz_localizes_naive_datetime(self):
        dt = datetime(2026, 1, 15, 12, 0, 0)
        localized = replace_tz(dt, "UTC")
        assert localized.tzinfo.zone == "UTC"
        assert localized.hour == 12

    def test_convert_to_timezone(self):
        dt = datetime(2026, 6, 1, 16, 0, tzinfo=timezone.utc)
        eastern = convert_to_timezone(dt, "Canada/Eastern")
        assert eastern.tzinfo.zone == "Canada/Eastern"
        expected = dt.astimezone(pytz.timezone("Canada/Eastern"))
        assert eastern == expected
