from typing import Dict

from .mappers import facebook_mapper
from .types import SourceConfig

source_configs: Dict[str, SourceConfig] = {
    "Facebook": SourceConfig(
        name="facebook",
        mapper_function=facebook_mapper,
        data_file_name="fb_posts.json",
    )
}
