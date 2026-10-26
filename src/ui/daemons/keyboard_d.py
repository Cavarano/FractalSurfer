"""A daemon responsible for handling user inputs."""

from threading import Event, Thread
from time import sleep, time
from typing import Never

from common.camera import Key
from ui.state import UIState

from .redraw_d import redraw


class KeyboardDaemon(Thread):
    """Daemon thread responsible for handling user inputs."""

    ui_state: UIState
    pressed_keys: set[Key]
    wakeup_event: Event

    def __init__(self) -> None:
        """Initialise `KeyboardDaemon`."""
        super().__init__(name="keyboard_daemon", daemon=True)
        self.wakeup_event = Event()
        self.pressed_keys = set()

    def add_key(self, key: Key) -> None:
        """Add a key to the set of pressed keys."""
        self.pressed_keys.add(key)
        self.wakeup_event.set()

    def remove_key(self, key: Key) -> None:
        """Remove a key from the set of pressed keys."""
        self.pressed_keys.discard(key)
        if not self.pressed_keys:
            self.wakeup_event.clear()

    def run(self) -> Never:
        """Start `KeyboardDaemon`."""
        # UI state needs to be set manually
        if not hasattr(self, "ui_state"):
            msg = "KeyboardDaemon.ui_state was not set"
            raise RuntimeError(msg)

        while True:
            self.wakeup_event.wait()
            self.ui_state.enable_movement_camera()

            while self.pressed_keys:
                pre_update = time()

                self.ui_state.camera = self.ui_state.camera.apply_movements(
                    self.pressed_keys,
                    self.ui_state.camera_params,
                )
                redraw()

                post_update = time()
                delta = post_update - pre_update
                stagger = self.ui_state.camera_params.polling_stagger - delta

                if stagger > 0.0:
                    sleep(stagger)

            self.ui_state.disable_movement_camera()
            redraw()


_DAEMON = KeyboardDaemon()


def start(ui_state: UIState) -> None:
    """Create and start `KeyboardDaemon`."""
    _DAEMON.ui_state = ui_state
    _DAEMON.start()


def add_key(key_id: int) -> None:
    """Add a key to the set of pressed keys."""
    _DAEMON.add_key(Key(key_id))


def remove_key(key_id: int) -> None:
    """Remove a key from the set of pressed keys."""
    _DAEMON.remove_key(Key(key_id))
