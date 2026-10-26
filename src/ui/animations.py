"""Utilities related to animations."""

from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from enum import Enum
from typing import override

from dearpygui import dearpygui as dpg

from common.camera import Camera
from common.reactive_params import ReactiveParams, WrappedSetattr

ADD_KF_BUTTON_TAG = "add_keyframe_button"


class AnimationMode(Enum):
    """Animation mode."""

    LINEAR = "linear"
    SPLINE = "spline"


class ExportFormat(Enum):
    """Export format for animations."""

    GIF = "gif"
    MP4 = "mp4"
    WEBM = "webm"


@dataclass
class AnimationParams(ReactiveParams):
    """Current state of animation params."""

    camera_access: Callable[[], Camera]
    animation_generator: Callable[[], str]
    animation_mode: AnimationMode = AnimationMode.LINEAR
    export_format: ExportFormat = ExportFormat.GIF
    keyframes: Sequence[Camera] = field(default_factory=list)
    frame_rate: int = 30

    def add_keyframe(self) -> None:
        """Add a keyframe to the animation."""
        self.keyframes = [*self.keyframes, self.camera_access()]
        dpg.configure_item(
            ADD_KF_BUTTON_TAG,
            label=f"add keyframe ({len(self.keyframes)} total)",
        )

    def clear_keyframes(self) -> None:
        """Remove all keyframes from the animation."""
        self.keyframes = []
        dpg.configure_item(
            ADD_KF_BUTTON_TAG,
            label=f"add keyframe ({len(self.keyframes)} total)",
        )

    @override
    def build_dpg_params(self, parent: str, setattr_: WrappedSetattr) -> None:
        dpg.add_combo(
            label="animation mode",
            items=[mode.value for mode in AnimationMode],
            default_value=self.animation_mode.value,
            callback=lambda _, x: setattr_(self, "animation_mode", AnimationMode(x)),
            parent=parent,
        )
        dpg.add_combo(
            label="export format",
            items=[fmt.value for fmt in ExportFormat],
            default_value=self.export_format.value,
            callback=lambda _, x: setattr_(self, "export_format", ExportFormat(x)),
            parent=parent,
        )
        dpg.add_slider_int(
            label="frame rate",
            min_value=1,
            max_value=60,
            default_value=self.frame_rate,
            callback=lambda _, x: setattr_(self, "frame_rate", x),
            parent=parent,
        )

        dpg.add_button(
            label="add keyframe (0 total)",
            tag=ADD_KF_BUTTON_TAG,
            callback=lambda: self.add_keyframe(),
            parent=parent,
        )

        dpg.add_button(
            label="clear keyframes",
            callback=lambda: self.clear_keyframes(),
            parent=parent,
        )

        def _generate_animation(txt_tag: str) -> None:
            dpg.set_value(txt_tag, "working...")
            msg = self.animation_generator()
            dpg.set_value(txt_tag, msg)

        with dpg.group(horizontal=True, parent=parent):
            txt_tag = "animation_txt_tag"
            dpg.add_button(
                label="export animation",
                callback=lambda: _generate_animation(txt_tag),
            )
            dpg.add_text("", tag=txt_tag)
