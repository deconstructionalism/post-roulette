import json
from typing import List

from ..types import MapRowToPost, PostData


def load_and_map_data(file_name: str, mapper_function: MapRowToPost) -> List[PostData]:
    """
    Load post data for a given platform from a JSON file that contains rows of
    dicts, and map over each row to return a `PostData` object via `map_row_to_post`
    function.
    """

    with open(f"./data/{file_name}", "r") as f:
        file = f.read()
        data = json.loads(file)

    return [mapper_function(index, row) for index, row in enumerate(data)]
