"""Widget responsible for displaying fractal textures."""

import numpy as np
from dearpygui import dearpygui as dpg

from common.types import Double, LUTtice
from ui.constants import SIDE_PANEL_WIDTH


class TexturePanel:
    """A child window for displaying fractal textures."""

    def __init__(self, vp_width: int, vp_height: int) -> None:
        """Initialise the texture panel with given viewport dimensions."""
        self.registry_tag = dpg.generate_uuid()
        self.width, self.height = self._adjust_size(vp_width, vp_height)

        self.window = dpg.add_child_window(
            width=self.width,
            height=self.height,
            menubar=False,
            border=False,
        )

        self._create_new_texture()

    @staticmethod
    def _adjust_size(width: int, height: int) -> tuple[int, int]:
        """Alter the viewport dimensions to account for padding."""
        padding_x = dpg.mvStyleVar_WindowPadding * 12
        padding_y = dpg.mvStyleVar_WindowPadding * 8
        return width - SIDE_PANEL_WIDTH - padding_x, height - padding_y

    def resize(self, vp_width: int, vp_height: int) -> None:
        """Resize the texture panel to match new viewport dimensions."""
        self.width, self.height = self._adjust_size(vp_width, vp_height)
        dpg.configure_item(self.window, width=self.width, height=self.height)
        self._create_new_texture()

    def _create_new_texture(self) -> None:
        """Create a new texture, deleting the previous one if needed."""
        if hasattr(self, "texture_tag"):
            dpg.delete_item(self.image_id)
            dpg.delete_item(self.texture_tag)

        self.texture_tag = dpg.generate_uuid()
        with dpg.texture_registry(tag=self.registry_tag):
            dpg.add_dynamic_texture(
                self.width,
                self.height,
                np.zeros((self.width * self.height * 4,), dtype=Double),  # type: ignore[reportArgumentType]
                tag=self.texture_tag,
            )

        self.image_id = dpg.add_image(
            self.texture_tag,
            width=self.width,
            height=self.height,
            parent=self.window,
        )

    def update(self, img: LUTtice) -> None:
        """Update the texture with a new image."""
        self.latest_image = img
        a = np.full((img.shape[0], img.shape[1], 1), 255, dtype=np.uint8)
        rgba = np.concatenate([img, a], axis=-1, dtype=np.uint8) / 255.0
        dpg.set_value(self.texture_tag, rgba.reshape(-1))
