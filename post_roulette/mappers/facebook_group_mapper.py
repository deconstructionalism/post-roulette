from ..lib import pretty_date_from_epoch_time
from ..types import PostData


def facebook_group_mapper(index: int, row: dict) -> PostData:
    """Map FB group post data dump row to `PostData`."""

    data = row.get("data", [{}])
    content = "" if len(data) == 0 else data[0].get("post", "")
    timestamp = int(row.get("timestamp", 0))

    return PostData(
        index=index,
        content=content,
        datetime=pretty_date_from_epoch_time(timestamp),
    )
