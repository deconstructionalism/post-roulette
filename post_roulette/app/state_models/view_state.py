from random import randrange
from typing import List, Optional

from tinydb.table import Document

from ...models import Cursors, Posts
from ...types import PostData
from . import PostState


class ViewState:
    """
    Handle all posts in current view along with current post and provide actions
    for manipulating the state, and control and query the database.
    """

    def __init__(
        self,
        source_name: str,
        cursors: Cursors,
        posts: Posts,
        mapped_posts: List[PostData],
    ) -> None:
        self.source_name = source_name
        self.cursors = cursors
        self.posts = posts
        self.mapped_posts = mapped_posts
        self.post = PostState()
        self.load_post()

    # ACCESSORS

    @property
    def cursor(self) -> int:
        """Current cursor index for data."""
        return self.cursors.get_value(self.source_name)

    @cursor.setter
    def cursor(self, value: int) -> None:
        self.cursors.set_value(self.source_name, value)

    @property
    def current_post_row(self) -> PostData:
        """Current row in data set selected by index."""
        return self.mapped_posts[self.cursor]

    @property
    def current_post(self) -> Optional[Document]:
        """Current post in DB selected by index, if it exists."""
        return self.posts.get(self.source_name, self.cursor)

    @property
    def has_next_post(self) -> bool:
        """Whether there is another post after this in post data."""
        return len(self.mapped_posts) - 1 > self.cursor

    @property
    def has_previous_post(self) -> bool:
        """Whether there is another post prior to this in post data."""
        return self.cursor > 0

    @property
    def is_post_saved(self) -> bool:
        """Whether post is saved in database."""
        return self.posts.get(self.source_name, self.cursor) is not None

    # ACTIONS

    def reset_cursor(self) -> None:
        """Reset cursor to start."""
        self.cursor = 0

    def random_post(self) -> None:
        """Load a random post."""
        self.cursor = randrange(0, len(self.mapped_posts) - 1)
        self.load_post()

    def load_post(self) -> None:
        """Load a post located at cursor."""
        self.post.load_post(self.current_post_row["content"])

    def next_post(self) -> None:
        """Load next post if it exists."""
        if self.has_next_post:
            self.cursor += 1
            self.load_post()

    def previous_post(self) -> None:
        """Load previous post if it exists."""
        if self.has_previous_post:
            self.cursor -= 1
            self.load_post()

    def toggle_post(self) -> None:
        """Save or delete current post from database."""
        if self.is_post_saved:
            self.posts.delete(self.source_name, self.cursor)
        else:
            self.posts.create(self.source_name, **self.current_post_row)
