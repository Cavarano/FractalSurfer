"""Callbacks for various UI elements."""

from typing import Any

from dearpygui import dearpygui as dpg

from common.types import Double
from ui.algo_choice import AlgoChoice

from .constants import TAB_BAR_TAG
from .daemons import add_key, redraw, remove_key
from .render import setattr_
from .state import UIState

Sender = int | str
AppData = tuple[Any, ...]


def on_viewport_resize(
    _sender: Sender,
    _app_data: AppData,
    ui_state: UIState,
) -> None:
    """Handle a viewport resize event."""
    new_width = dpg.get_viewport_width()
    new_height = dpg.get_viewport_height()
    ui_state.handle_resize(new_width, new_height)

    redraw()


_JULIA_SET_CONST: tuple[Double, Double] | None = None


def on_tab_change(
    _sender: Sender,
    _app_data: AppData,
    ui_state: UIState,
) -> None:
    """Handle a tab change event."""
    new_tab_id = dpg.get_value(TAB_BAR_TAG)
    new_tab_tag: str = dpg.get_item_label(new_tab_id)  # type: ignore[reportAssignmentType]

    # remove all children
    dpg.delete_item(item=new_tab_tag, children_only=True)

    # create the new contents
    ui_state.replace_algo(new_tab_tag)

    # if Julia, check if _JULIA_SET_CONST is set
    global _JULIA_SET_CONST  # noqa: PLW0603
    if new_tab_tag == AlgoChoice.JULIA.value and _JULIA_SET_CONST is not None:
        ui_state.algo_params.mandelbrot_const_re = _JULIA_SET_CONST[0]  # type: ignore[reportAttributeAccessIssue]
        ui_state.algo_params.mandelbrot_const_im = _JULIA_SET_CONST[1]  # type: ignore[reportAttributeAccessIssue]
        _JULIA_SET_CONST = None

    ui_state.algo_params.build_dpg_params(new_tab_tag, setattr_)

    # special: additional button for Mandelbrot
    if new_tab_tag == AlgoChoice.MANDELBROT.value:
        dpg.add_button(
            label="go to corresponding Julia set",
            callback=on_mandelbrot_to_julia,
            user_data=ui_state,
            parent=new_tab_tag,
        )

    # update coords label by applying no movements
    ui_state.camera.apply_movements(set(), ui_state.camera_params)

    # reset animation parameters
    ui_state.animation_params.clear_keyframes()

    redraw()


def on_mandelbrot_to_julia(
    _sender: Sender,
    _app_data: AppData,
    ui_state: UIState,
) -> None:
    """Handle a Mandelbrot to Julia set transition."""
    global _JULIA_SET_CONST  # noqa: PLW0603
    _JULIA_SET_CONST = ui_state.camera.center_xy()
    dpg.set_value(TAB_BAR_TAG, AlgoChoice.JULIA.value)


def on_key_down(
    _sender: Sender,
    app_data: AppData,
) -> None:
    """Signal that a key is being held down."""
    add_key(app_data[0])  # type: ignore[reportArgumentType]


def on_key_release(
    _sender: Sender,
    app_data: AppData,
) -> None:
    """Signal that a key was released."""
    remove_key(app_data)  # type: ignore[reportArgumentType]


def on_key_press(
    _sender: Sender,
    app_data: AppData,
) -> None:
    """Signal that a key was pressed."""
    add_key(app_data)  # type: ignore[reportArgumentType]
