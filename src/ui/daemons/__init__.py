"""Daemons responsible for handling I/O operations."""

from ui.state import UIState

from . import keyboard_d, redraw_d
from .keyboard_d import add_key, remove_key  # noqa: F401
from .redraw_d import redraw  # noqa: F401


def start_daemons(ui_state: UIState) -> None:
    """Start all UI daemon threads."""
    redraw_d.start(ui_state)
    keyboard_d.start(ui_state)
