import importlib
import json
from typing import List

from ..types import PostData


def load_and_map_data(file_name: str, mapper_function_name: str) -> List[PostData]:
    """
    Load post data for a given platform from a JSON file that contains rows of
    dicts, and map over each row to return a `PostData` object via `map_row_to_post`
    function.
    """

    mappers = importlib.import_module("post_roulette.mappers")
    mapper_function = getattr(mappers, mapper_function_name)

    with open(f"./data/{file_name}", "r") as f:
        file = f.read()
        data = json.loads(file)

    return [mapper_function(index, row) for index, row in enumerate(data)]
