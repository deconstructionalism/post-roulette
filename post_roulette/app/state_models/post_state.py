from functools import reduce
from typing import List, Tuple

from ...config import ViewConfig
from ...lib.view_helpers import wrap_text


class PostState:
    """
    Handle a single post's content, content pagination, and provide actions
    for manipulating the post pages.
    """

    def __init__(self) -> None:
        self.pages: List[str] = [""]
        self.cursor: int = 0

    # ACCESSORS

    @property
    def current_page(self) -> str:
        """Text from current page of post."""
        return self.pages[self.cursor]

    @property
    def has_next_post_page(self) -> bool:
        """Whether there is another page after this in post pages."""
        return self.cursor < len(self.pages) - 1

    @property
    def has_previous_post_page(self) -> bool:
        """Whether there is page before this in post pages."""
        return self.cursor > 0

    # ACTIONS

    def increment_post_page(self):
        """Load the next page if it exists."""
        if self.has_next_post_page:
            self.cursor += 1

    def decrement_post_page(self):
        """Load the previous page if it exists."""
        if self.has_previous_post_page:
            self.cursor -= 1

    def load_post(self, post_text: str):
        """Load a page from text."""

        wrapped_text = wrap_text(post_text, 6)
        wrapped_lines = wrapped_text.split("\n")

        def reducer(acc: List[str], next: Tuple[int, str]) -> List[str]:
            """
            Reduce `wrapped_lines` to a list of pages, each of which will fit
            into the line height of a post content box.
            """

            next_index, next_line = next
            return (
                [*acc, next_line]
                if next_index % (ViewConfig.CARD_HEIGHT - 9) == 0
                else [*acc[:-1], "\n".join([acc[-1], next_line])]
            )

        self.cursor = 0
        self.pages = reduce(reducer, enumerate(wrapped_lines), [])
