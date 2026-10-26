"""The entrypoint for `FractalSurfer`."""

from dearpygui import dearpygui as dpg

import ui.callbacks as cb
from common.camera import Key
from ui.constants import MIN_HEIGHT, MIN_WIDTH, SIDE_PANEL_WIDTH, TAB_BAR_TAG
from ui.daemons import start_daemons
from ui.render import (
    render_animation_params,
    render_camera_params,
    render_colour_params,
    render_initial_tab_bar,
)
from ui.state import UIState
from ui.widgets import TexturePanel


def build_ui() -> None:
    """Build the user interface."""
    ui_state = UIState()

    dpg.create_context()
    dpg.create_viewport(
        title="FractalSurfer",
        min_width=MIN_WIDTH,
        min_height=MIN_HEIGHT,
        width=MIN_WIDTH,
        height=MIN_HEIGHT,
        resizable=True,
    )
    dpg.setup_dearpygui()

    with (
        dpg.window() as main_window,
        dpg.group(horizontal=True),
    ):
        texture_panel = TexturePanel(
            MIN_WIDTH,
            MIN_HEIGHT,
        )
        ui_state.set_texture_panel(texture_panel)

        with dpg.child_window(width=SIDE_PANEL_WIDTH):
            dpg.add_text("WASD to move, Q/E to zoom in/out")

            with dpg.tab_bar(
                tag=TAB_BAR_TAG,
                callback=cb.on_tab_change,
                user_data=ui_state,
            ):
                render_initial_tab_bar(ui_state)

            dpg.add_spacer(height=5)
            dpg.add_separator()

            with dpg.child_window(  # added for padding
                border=False,
                auto_resize_y=True,
            ):
                render_camera_params(ui_state)

            dpg.add_spacer(height=5)
            dpg.add_separator()

            with dpg.child_window(  # same here
                border=False,
                auto_resize_y=True,
            ):
                render_animation_params(ui_state)

            dpg.add_spacer(height=5)
            dpg.add_separator()

            with dpg.child_window(  # and here
                border=False,
                auto_resize_y=True,
            ):
                render_colour_params(ui_state)

    movement_keys = [Key.UP, Key.DOWN, Key.LEFT, Key.RIGHT, Key.ZOOM_IN, Key.ZOOM_OUT]

    with dpg.handler_registry():
        for key in movement_keys:
            dpg.add_key_down_handler(key.value, callback=cb.on_key_down)
            dpg.add_key_release_handler(key.value, callback=cb.on_key_release)
            dpg.add_key_press_handler(key.value, callback=cb.on_key_press)

    dpg.set_viewport_resize_callback(cb.on_viewport_resize, user_data=ui_state)

    dpg.set_primary_window(window=main_window, value=True)
    dpg.show_viewport()

    start_daemons(ui_state)
    dpg.start_dearpygui()

    dpg.destroy_context()
