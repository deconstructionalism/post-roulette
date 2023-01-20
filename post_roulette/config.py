from typing import Dict

from .types import SourceConfig

source_configs: Dict[str, SourceConfig] = {
    "Facebook": SourceConfig(
        name="facebook",
        mapper_function_name="facebook_mapper",
        data_file_name="fb_posts.json",
    )
}


class ViewConfig:
    PADDING_LEFT: int = 2
    PADDING_TOP: int = 1
    WIDTH: int = 100
    CARD_HEIGHT: int = 20

    # NOTE: KEY assignments should be alphabetical; special keys will not work.
    NEXT_POST_KEY: str = "M"
    PREV_POST_KEY: str = "N"
    TOGGLE_POST_KEY: str = "T"
    RANDOM_POST_KEY: str = "R"
    NEXT_PAGE_KEY: str = "L"
    PREV_PAGE_KEY: str = "K"
    QUIT_KEY: str = "Q"
    RESET_CURSOR_KEY: str = "C"
