import curses
import textwrap
from curses import window, wrapper
from functools import reduce
from random import randrange
from typing import List, Optional, Tuple

from tinydb.table import Document

from ..models import Cursors, Posts
from ..types import PostData


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

        wrapped_text = View._wrap_text(post_text, 6)
        wrapped_lines = wrapped_text.split("\n")

        def reducer(acc: List[str], next: Tuple[int, str]) -> List[str]:
            """
            Reduce `wrapped_lines` to a list of pages, each of which will fit
            into the line height of a post content box.
            """

            next_index, next_line = next
            return (
                [*acc, next_line]
                if next_index % (View.CARD_HEIGHT - 9) == 0
                else [*acc[:-1], "\n".join([acc[-1], next_line])]
            )

        self.cursor = 0
        self.pages = reduce(reducer, enumerate(wrapped_lines), [])


class View:
    """
    Provide configurable `curses` views for the app to jog through posts as
    well as actions to interact with views, and control and query the database.
    """

    # VIEW CONFIG
    # NOTE: KEY assignments should be alphabetical; special keys will not work.

    PADDING_LEFT = 2
    PADDING_TOP = 1
    WIDTH = 100
    CARD_HEIGHT = 20
    NEXT_POST_KEY = "M"
    PREV_POST_KEY = "N"
    TOGGLE_POST_KEY = "T"
    RANDOM_POST_KEY = "R"
    NEXT_PAGE_KEY = "L"
    PREV_PAGE_KEY = "K"
    QUIT_KEY = "Q"
    RESET_CURSOR_KEY = "C"

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
        self.main_window: window
        self.post_state = PostState()
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
        self.post_state.load_post(self.current_post_row["content"])

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

    # HELPER METHODS

    @staticmethod
    def _wrap_text(text: str, additional_padding=0) -> str:
        """Wrap text to fit inside of app width."""
        return textwrap.fill(text, View.WIDTH - additional_padding)

    @staticmethod
    def _is_key(key: int, value: str) -> bool:
        """
        For an alphabetical key int, check that it case-insensitive matches a given
        letter.

        NOTE: This only works with alphabetical keys; special keys will not work.
        """
        return key in [ord(value.lower()), ord(value.upper())]

    # INPUT HANDLERS

    def _handle_sanitize_cursor_input(self) -> bool:
        """
        Input handler for sanitize cursor view.

        Prompt user to either sanitize the cursor and continue, or quit the app.
        """

        # Value returned by function. If cursor needs to be reset,
        # this value will be set to `True` so calling context will know
        # to exit curses view
        quit_after = False

        while True:
            key = self.main_window.getch()

            # handle continue action
            if View._is_key(key, View.RESET_CURSOR_KEY):
                self.reset_cursor()
                break

            # handle quit action
            if View._is_key(key, View.QUIT_KEY):
                quit_after = True
                break

        return quit_after

    def _handle_main_view_input(self) -> bool:
        """
        Input handler for main view.

        Allow user to jog through post, post pages, save and drop posts from database
        randomize their post selection, or quit.
        """

        # Value returned by function. If exit action is taken, value
        # will be set to `True` so calling context will know to
        # exit curses view
        quit_after = False

        while True:
            key = self.main_window.getch()

            # handle quit action
            if View._is_key(key, View.QUIT_KEY):
                quit_after = True
                break

            # handle next post action
            if self.has_next_post and View._is_key(key, View.NEXT_POST_KEY):
                self.next_post()
                break

            # handle previous post action
            if self.has_previous_post and View._is_key(key, View.PREV_POST_KEY):
                self.previous_post()
                break

            # handle next post page action
            if self.post_state.has_next_post_page and View._is_key(
                key, View.NEXT_PAGE_KEY
            ):
                self.post_state.increment_post_page()
                break

            # handle previous post page action
            if self.post_state.has_previous_post_page and View._is_key(
                key, View.PREV_PAGE_KEY
            ):
                self.post_state.decrement_post_page()
                break

            # handle toggle action
            if View._is_key(key, View.TOGGLE_POST_KEY):
                self.toggle_post()
                break

            # handle random action
            if View._is_key(key, View.RANDOM_POST_KEY):
                self.random_post()
                break

        return quit_after

    # CURSES RENDERERS

    def _render_sanitize_cursor(self) -> bool:
        """
        If cursor is out of range for data, render view that allows
        user to either exit program or set cursor position to 0 and
        continue to main view.
        """

        # Value returned by function. If exit action is taken, value
        # will be set to `True` so calling context will know to
        # exit curses view
        quit_after = False

        # determine if cursor is within range for data
        if self.cursor not in range(0, len(self.mapped_posts) - 1):

            warning_content_box = self.main_window.subwin(
                20, View.WIDTH, View.PADDING_TOP, View.PADDING_LEFT
            )
            text = (
                f"WARNING: Previous position for {self.source_name} posts set "
                + "to {self.cursor}, which is out of range for post data. "
            )

            warning_content_box.addstr(0, 0, self._wrap_text(text))
            warning_content_box.addstr(
                4,
                0,
                self._wrap_text(
                    f"Press {View.RESET_CURSOR_KEY} to reset index to 0 and continue"
                ),
                curses.A_BOLD,
            )
            warning_content_box.addstr(
                6,
                0,
                self._wrap_text(f"Press {View.QUIT_KEY} to exit"),
                curses.A_BOLD,
            )

            quit_after = self._handle_sanitize_cursor_input()

        return quit_after

    def _render_header(self) -> None:
        """Render app header for main view."""

        text = f"POST ROULETTE: {self.source_name.upper()}"
        self.main_window.addstr(
            View.PADDING_TOP,
            View.PADDING_LEFT,
            text.center(View.WIDTH - 1),
            curses.A_STANDOUT,
        )

    def _render_post(self) -> None:
        """Render current post for main view."""

        text_card_border = self.main_window.subwin(
            View.CARD_HEIGHT,
            View.WIDTH,
            View.PADDING_TOP + 1,
            View.PADDING_LEFT,
        )
        text_card_content = self.main_window.subwin(
            View.CARD_HEIGHT - 2,
            View.WIDTH - 4,
            View.PADDING_TOP + 2,
            View.PADDING_LEFT + 2,
        )
        text_card_border.box()

        index_text = "{} / {}{}".format(
            self.cursor + 1,
            len(self.mapped_posts),
            " ✔" if self.is_post_saved else "",
        )

        text_card_content.addstr(
            0, 0, View._wrap_text(self.current_post_row["datetime"], 5)
        )
        text_card_content.addstr(
            2,
            0,
            View._wrap_text(index_text, 6),
            curses.A_STANDOUT if self.is_post_saved else curses.A_DIM,
        )
        text_card_content.addstr(
            4,
            0,
            self.post_state.current_page,
            5,
        )

        # render controls and pagination if post has more than one page
        if len(self.post_state.pages) > 1:

            page_index_text = (
                f"Page {self.post_state.cursor + 1} / {len(self.post_state.pages)}"
            )
            next_page_text = f"Next Page ({View.NEXT_PAGE_KEY})"
            previous_page_text = f"Previous Page ({View.PREV_PAGE_KEY})"
            control_text = f" {next_page_text} | {previous_page_text} "
            control_text_x = View.WIDTH - 4 - len(control_text)

            text_card_content.addstr(View.CARD_HEIGHT - 4, 0, page_index_text, 5)
            text_card_content.addstr(
                View.CARD_HEIGHT - 4, control_text_x, control_text, curses.A_BOLD
            )

            # Dim non-active controls
            if not self.post_state.has_next_post_page:
                text_card_content.addnstr(
                    View.CARD_HEIGHT - 4,
                    control_text.index(next_page_text) + control_text_x,
                    next_page_text,
                    curses.A_DIM,
                )
            if not self.post_state.has_previous_post_page:
                text_card_content.addnstr(
                    View.CARD_HEIGHT - 4,
                    control_text.index(previous_page_text) + control_text_x,
                    previous_page_text,
                    curses.A_DIM,
                )

    def _render_controls(self) -> None:
        "Render active controls for main view."

        next_text = f"Next ({View.NEXT_POST_KEY})"
        prev_text = f"Prev ({View.PREV_POST_KEY})"
        toggle_text = (
            f"{'Drop' if self.is_post_saved else 'Save'} ({View.TOGGLE_POST_KEY})"
        )
        random_text = f"Rand ({View.RANDOM_POST_KEY})"
        quit_text = f"Quit ({View.QUIT_KEY})"
        text = (
            f" {prev_text} | {toggle_text} | {next_text} | {random_text} | {quit_text} "
        )

        control_content = self.main_window.subwin(
            1,
            View.WIDTH,
            View.PADDING_TOP + View.CARD_HEIGHT + 1,
            View.PADDING_LEFT,
        )

        control_content.addstr(0, 0, text, curses.A_BOLD)

        # Dim non-active controls
        if not self.has_next_post:
            control_content.addnstr(0, text.index(next_text), next_text, curses.A_DIM)
        if not self.has_previous_post:
            control_content.addnstr(0, text.index(prev_text), prev_text, curses.A_DIM)

    def _render_main_view(self) -> bool:
        """Render main view."""

        self.main_window.clear()
        self._render_header()
        self._render_post()
        self._render_controls()

        return self._handle_main_view_input()

    def _render(self, main_window: window) -> None:
        """Render the app."""

        self.main_window = main_window

        quit_after = self._render_sanitize_cursor()
        if quit_after:
            return

        while True:
            quit_after = self._render_main_view()
            if quit_after:
                break

    def render(self) -> None:
        """Wrap `_render` class method with `curses` convenience wrapper."""

        return wrapper(self._render)
