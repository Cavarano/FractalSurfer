"""Utilities related to UI lifecycle."""

from datetime import datetime
from typing import Any

from dearpygui import dearpygui as dpg
from PIL import Image

from .algo_choice import AlgoChoice
from .constants import SCREENSHOT_FOLDER
from .daemons import redraw
from .state import UIState
from .utils import lazy_chain


def setattr_(obj: Any, target: str, value: Any) -> None:  # noqa: ANN401
    """Invoke `setattr` and fire off a redraw event."""
    setattr(obj, target, value)
    redraw()


def render_initial_tab_bar(ui_state: UIState) -> None:
    """Render the tab bar, listing each fractal algorithm."""
    for i, algo in enumerate(AlgoChoice.list_algorithms()):
        tab_id = str(dpg.add_tab(label=algo, tag=algo))
        # draw the first tab immediately
        if i == 0:
            # circular import prevention
            from .callbacks import on_mandelbrot_to_julia  # noqa: PLC0415

            ui_state.algo_params.build_dpg_params(tab_id, setattr_)
            dpg.add_button(
                label="go to corresponding Julia set",
                callback=on_mandelbrot_to_julia,
                user_data=ui_state,
                parent=tab_id,
            )


def render_camera_params(ui_state: UIState) -> None:
    """Render the camera settings."""
    with dpg.collapsing_header(
        label="camera settings",
        default_open=True,
    ) as parent:
        dpg.add_button(
            label="reset camera",
            callback=lambda: lazy_chain(ui_state.reset_camera, redraw)(),
        )

        with dpg.group(horizontal=True):
            label_tag = "screenshot_label"
            dpg.add_button(
                label="save screenshot",
                callback=lambda: _screenshot(ui_state, label_tag),
            )
            dpg.add_text(tag=label_tag)

        ui_state.camera_params.build_dpg_params(parent, setattr_)
        # update coords label by applying no movements
        ui_state.camera.apply_movements(set(), ui_state.camera_params)


def _screenshot(ui_state: UIState, label_tag: str) -> None:
    filename = f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.png"  # noqa: DTZ005

    Image.fromarray(
        ui_state.texture_panel.latest_image,
        mode="RGB",
    ).save(
        SCREENSHOT_FOLDER / filename,
    )

    dpg.set_value(label_tag, f"saved {filename}")


def render_colour_params(ui_state: UIState) -> None:
    """Render the colour settings."""
    with dpg.collapsing_header(
        label="colours",
        default_open=True,
    ) as parent:
        ui_state.colour_params.build_dpg_params(parent, setattr_)


def render_animation_params(ui_state: UIState) -> None:
    """Render the animation settings."""
    with dpg.collapsing_header(
        label="animations",
        default_open=True,
    ) as parent:
        ui_state.animation_params.build_dpg_params(parent, setattr_)
