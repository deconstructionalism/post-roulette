import textwrap

from ..config import ViewConfig


def wrap_text(text: str, additional_padding=0) -> str:
    """Wrap text to fit inside of app width."""
    return textwrap.fill(text, ViewConfig.WIDTH - additional_padding)


def is_key(key: int, value: str) -> bool:
    """
    For an alphabetical key int, check that it case-insensitive matches a given
    letter.

    NOTE: This only works with alphabetical keys; special keys will not work.
    """
    return key in [ord(value.lower()), ord(value.upper())]
