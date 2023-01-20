import curses

from ...config import ViewConfig
from ...lib.view_helpers import is_key, wrap_text
from ..app import App


class MainView:
    """
    Main curses view for jogging through and interacting with posts.
    """

    def __init__(self, app: App) -> None:
        self.app = app

    # INPUT HANDLERS

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
            key = self.app.window.getch()

            # handle quit action
            if is_key(key, ViewConfig.QUIT_KEY):
                quit_after = True
                break

            # handle next post action
            if self.app.view.has_next_post and is_key(key, ViewConfig.NEXT_POST_KEY):
                self.app.view.next_post()
                break

            # handle previous post action
            if self.app.view.has_previous_post and is_key(
                key, ViewConfig.PREV_POST_KEY
            ):
                self.app.view.previous_post()
                break

            # handle next post page action
            if self.app.view.post.has_next_post_page and is_key(
                key, ViewConfig.NEXT_PAGE_KEY
            ):
                self.app.view.post.increment_post_page()
                break

            # handle previous post page action
            if self.app.view.post.has_previous_post_page and is_key(
                key, ViewConfig.PREV_PAGE_KEY
            ):
                self.app.view.post.decrement_post_page()
                break

            # handle toggle action
            if is_key(key, ViewConfig.TOGGLE_POST_KEY):
                self.app.view.toggle_post()
                break

            # handle random action
            if is_key(key, ViewConfig.RANDOM_POST_KEY):
                self.app.view.random_post()
                break

        return quit_after

    # CURSES RENDERERS

    def _render_header(self) -> None:
        """Render app header for main view."""

        text = f"POST ROULETTE: {self.app.source_name.upper()}"
        self.app.window.addstr(
            ViewConfig.PADDING_TOP,
            ViewConfig.PADDING_LEFT,
            text.center(ViewConfig.WIDTH - 1),
            curses.A_STANDOUT,
        )

    def _render_post(self) -> None:
        """Render current post for main view."""

        text_card_border = self.app.window.subwin(
            ViewConfig.CARD_HEIGHT,
            ViewConfig.WIDTH,
            ViewConfig.PADDING_TOP + 1,
            ViewConfig.PADDING_LEFT,
        )
        text_card_content = self.app.window.subwin(
            ViewConfig.CARD_HEIGHT - 2,
            ViewConfig.WIDTH - 4,
            ViewConfig.PADDING_TOP + 2,
            ViewConfig.PADDING_LEFT + 2,
        )
        text_card_border.box()

        index_text = "{} / {}{}".format(
            self.app.view.cursor + 1,
            len(self.app.view.mapped_posts),
            " ✔" if self.app.view.is_post_saved else "",
        )

        text_card_content.addstr(
            0, 0, wrap_text(self.app.view.current_post_row["datetime"], 5)
        )
        text_card_content.addstr(
            2,
            0,
            wrap_text(index_text, 6),
            curses.A_STANDOUT if self.app.view.is_post_saved else curses.A_DIM,
        )
        text_card_content.addstr(
            4,
            0,
            self.app.view.post.current_page,
            5,
        )

        # render controls and pagination if post has more than one page
        if len(self.app.view.post.pages) > 1:

            page_index_text = (
                f"Page {self.app.view.post.cursor + 1} / "
                + f"{len(self.app.view.post.pages)}"
            )
            next_page_text = f"Next Page ({ViewConfig.NEXT_PAGE_KEY})"
            previous_page_text = f"Previous Page ({ViewConfig.PREV_PAGE_KEY})"
            control_text = f" {previous_page_text} | {next_page_text} "
            control_text_x = ViewConfig.WIDTH - 4 - len(control_text)

            text_card_content.addstr(ViewConfig.CARD_HEIGHT - 4, 0, page_index_text, 5)
            text_card_content.addstr(
                ViewConfig.CARD_HEIGHT - 4, control_text_x, control_text, curses.A_BOLD
            )

            # Dim non-active controls
            if not self.app.view.post.has_next_post_page:
                text_card_content.addnstr(
                    ViewConfig.CARD_HEIGHT - 4,
                    control_text.index(next_page_text) + control_text_x,
                    next_page_text,
                    curses.A_DIM,
                )
            if not self.app.view.post.has_previous_post_page:
                text_card_content.addnstr(
                    ViewConfig.CARD_HEIGHT - 4,
                    control_text.index(previous_page_text) + control_text_x,
                    previous_page_text,
                    curses.A_DIM,
                )

    def _render_controls(self) -> None:
        "Render active controls for main view."

        next_text = f"Next ({ViewConfig.NEXT_POST_KEY})"
        prev_text = f"Prev ({ViewConfig.PREV_POST_KEY})"
        toggle_text = (
            f"{'Drop' if self.app.view.is_post_saved else 'Save'} "
            + f"({ViewConfig.TOGGLE_POST_KEY})"
        )
        random_text = f"Rand ({ViewConfig.RANDOM_POST_KEY})"
        quit_text = f"Quit ({ViewConfig.QUIT_KEY})"
        text = (
            f" {prev_text} | {toggle_text} | {next_text} | {random_text} | {quit_text} "
        )

        control_content = self.app.window.subwin(
            1,
            ViewConfig.WIDTH,
            ViewConfig.PADDING_TOP + ViewConfig.CARD_HEIGHT + 1,
            ViewConfig.PADDING_LEFT,
        )

        control_content.addstr(0, 0, text, curses.A_BOLD)

        # Dim non-active controls
        if not self.app.view.has_next_post:
            control_content.addnstr(0, text.index(next_text), next_text, curses.A_DIM)
        if not self.app.view.has_previous_post:
            control_content.addnstr(0, text.index(prev_text), prev_text, curses.A_DIM)

    def render(self) -> bool:
        """Render the view."""

        self.app.window.clear()
        self._render_header()
        self._render_post()
        self._render_controls()

        return self._handle_main_view_input()
