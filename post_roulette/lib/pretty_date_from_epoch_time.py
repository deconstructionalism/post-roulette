from datetime import datetime, timezone
from zoneinfo import ZoneInfo


def pretty_date_from_epoch_time(epoch_time: int, zone="America/New_York") -> str:
    """
    Convert epoch time to local time zone string.
    """

    date = datetime.fromtimestamp(epoch_time)
    date.replace(tzinfo=timezone.utc)
    local = date.astimezone(tz=ZoneInfo(zone))

    return local.strftime("%m/%d/%Y, %H:%M:%S")
