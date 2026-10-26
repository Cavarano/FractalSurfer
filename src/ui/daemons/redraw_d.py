"""A daemon responsible for redrawing the UI texture panel."""

from threading import Event, Thread
from typing import Never

from ui.state import UIState


class RedrawDaemon(Thread):
    """Daemon thread responsible for redrawing the UI texture panel."""

    redraw_event: Event
    ui_state: UIState

    def __init__(self) -> None:
        """Initialise `RedrawDaemon`."""
        super().__init__(name="redraw_daemon", daemon=True)
        self.redraw_event = Event()

    def signal(self) -> None:
        """Signal the thread to commence redraw routine."""
        self.redraw_event.set()

    def run(self) -> Never:
        """Start `RedrawDaemon`."""
        # UI state needs to be set manually
        if not hasattr(self, "ui_state"):
            msg = "RedrawDaemon.ui_state was not set"
            raise RuntimeError(msg)

        while True:
            self.redraw_event.wait()
            old_dims = self.ui_state.camera.width, self.ui_state.camera.height

            luttice = self.ui_state.generate_frame()

            new_dims = self.ui_state.camera.width, self.ui_state.camera.height

            # if dims did not change mid-update, apply
            if old_dims == new_dims:
                self.ui_state.texture_panel.update(luttice)
                self.redraw_event.clear()


_DAEMON = RedrawDaemon()


def redraw() -> None:
    """Fire a redraw event."""
    _DAEMON.signal()


def start(ui_state: UIState) -> None:
    """Create and start `RedrawDaemon`."""
    _DAEMON.ui_state = ui_state
    _DAEMON.start()

    redraw()
