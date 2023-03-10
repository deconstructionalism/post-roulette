from typing import Any, Callable, TypedDict


class PostData(TypedDict):
    index: int
    content: str
    datetime: str


MapRowToPost = Callable[[int, Any], PostData]


class SourceConfig(TypedDict):
    name: str
    mapper_function_name: str
    data_file_name: str
