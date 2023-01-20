import curses

from ...config import ViewConfig
from ...lib.view_helpers import is_key, wrap_text
from .. import App


class SanitizeCursorView:
    """
    If cursor is out of range for data, render view that allows
    user to either exit program or set cursor position to 0 and
    continue to main view.
    """

    def __init__(self, app: App):
        self.app = app

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
            key = self.app.window.getch()

            # handle continue action
            if is_key(key, ViewConfig.RESET_CURSOR_KEY):
                self.app.view.reset_cursor()
                break

            # handle quit action
            if is_key(key, ViewConfig.QUIT_KEY):
                quit_after = True
                break

        return quit_after

    # CURSES RENDERERS

    def render(self) -> bool:
        """Render the view."""

        # Value returned by function. If exit action is taken, value
        # will be set to `True` so calling context will know to
        # exit curses view
        quit_after = False

        # determine if cursor is within range for data
        if self.app.view.cursor not in range(0, len(self.app.view.mapped_posts) - 1):

            warning_content_box = self.app.window.subwin(
                20, ViewConfig.WIDTH, ViewConfig.PADDING_TOP, ViewConfig.PADDING_LEFT
            )
            text = (
                f"WARNING: Previous position for {self.app.source_name} posts set "
                + f"to {self.app.view.cursor}, which is out of range for post data. "
            )

            warning_content_box.addstr(0, 0, wrap_text(text))
            warning_content_box.addstr(
                4,
                0,
                wrap_text(
                    f"Press {ViewConfig.RESET_CURSOR_KEY} to reset index to 0 "
                    + "and continue"
                ),
                curses.A_BOLD,
            )
            warning_content_box.addstr(
                6,
                0,
                wrap_text(f"Press {ViewConfig.QUIT_KEY} to exit"),
                curses.A_BOLD,
            )

            quit_after = self._handle_sanitize_cursor_input()

        return quit_after
