import json
from curses import window, wrapper
from typing import List

from ..models import Cursors, Posts
from ..types import PostData
from .state_models import ViewState


class App:
    """
    Render the views for the UI.
    """

    def __init__(
        self,
        source_name: str,
        cursors: Cursors,
        posts: Posts,
        mapped_posts: List[PostData],
        in_debugging_mode: bool = False,
    ) -> None:
        self.source_name = source_name
        self.in_debugging_mode = in_debugging_mode
        self.window: window
        self.view = ViewState(source_name, cursors, posts, mapped_posts)

    def _render(self, window: window) -> None:
        """Render the app."""

        # avoids circular imports
        from .views import MainView, SanitizeCursorView

        self.window = window
        sanitize_cursor_view = SanitizeCursorView(self)
        main_view = MainView(self)

        quit_after = sanitize_cursor_view.render()
        if quit_after:
            return

        while True:
            quit_after = main_view.render()
            if quit_after:
                break

    def render(self) -> None:
        """Wrap `_render` class method with `curses` convenience wrapper."""

        # in debugging mode, print the current selected posts data JSON and exit
        if self.in_debugging_mode:
            print("DEBUG MODE – CURRENT POST AT INDEX:\n")
            print(json.dumps(self.view.current_post_row, indent=4))
            return

        return wrapper(self._render)
