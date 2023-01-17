__version__ = "0.1.0"

import argparse

from tinydb import TinyDB

from .config import source_configs
from .lib import View, load_and_map_data
from .models import Cursors, Posts


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="post-roulette",
        description=(
            "A simple, probably over-built `curses` app that loads and "
            + "displays post data from various social media data dumps so that "
            + "a user can jog thru and select posts to save in a local JSON DB."
        ),
    )

    parser.add_argument(
        "config_name",
        choices=source_configs.keys(),
        help="choose a configuration to run",
    )

    args = parser.parse_args()
    source_config = source_configs[args.config_name]

    db = TinyDB("./db/db.json")
    cursors = Cursors(db)
    posts = Posts(db)
    mapped_posts = load_and_map_data(
        source_config["data_file_name"], source_config["mapper_function"]
    )

    view = View(source_config["name"], cursors, posts, mapped_posts)

    view.render()
