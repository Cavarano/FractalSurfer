"""Colour palette parameters & utilities."""

from dataclasses import dataclass
from enum import Enum
from functools import partial
from typing import override

import numpy as np
from dearpygui import dearpygui as dpg

from common.reactive_params import ReactiveParams, WrappedSetattr
from common.types import Double, Lattice, LUTtice

from .utils import lazy_chain

Cutoff = float
Colour = tuple[float, float, float]

PresetStop = tuple[Cutoff, Colour]
Preset = list[PresetStop]


PRESETS: dict[str, Preset] = {
    "classic": [
        (0.00, (0.0, 0.0, 0.0)),
        (0.16, (0.0, 0.0, 0.5)),
        (0.42, (0.0, 0.5, 0.0)),
        (0.64, (0.8, 0.8, 0.0)),
        (0.86, (1.0, 0.4, 0.0)),
        (1.00, (1.0, 1.0, 1.0)),
    ],
    "fire": [
        (0.00, (0.0, 0.0, 0.0)),
        (0.30, (0.4, 0.0, 0.1)),
        (0.60, (0.9, 0.2, 0.0)),
        (0.85, (1.0, 0.8, 0.2)),
        (1.00, (1.0, 1.0, 1.0)),
    ],
    "ice": [
        (0.00, (0.0, 0.0, 0.0)),
        (0.30, (0.0, 0.2, 0.5)),
        (0.60, (0.2, 0.6, 1.0)),
        (0.90, (0.8, 0.95, 1.0)),
        (1.00, (1.0, 1.0, 1.0)),
    ],
    "neon": [
        (0.00, (0.0, 0.0, 0.0)),
        (0.25, (0.2, 1.0, 0.4)),
        (0.50, (1.0, 0.2, 0.8)),
        (0.75, (0.2, 0.8, 1.0)),
        (1.00, (1.0, 1.0, 1.0)),
    ],
}


CUSTOM_STOPS_DEFAULT: list[PresetStop] = [
    (0.0, (0.0, 0.0, 0.0)),
    (0.5, (0.0, 0.5, 1.0)),
    (1.0, (1.0, 1.0, 1.0)),
]

CUSTOM_COLOURS_GROUP_TAG = "CCGtag"


class PaletteMode(Enum):
    """Colour palette mode."""

    PRESET = "preset"
    CUSTOM = "custom"


@dataclass
class ColourParams(ReactiveParams):
    """Current state of colour params."""

    palette_mode: PaletteMode = PaletteMode.PRESET
    chosen_preset: str = "classic"
    gamma: float = 1.0

    def apply_lut(self, lat: Lattice, max_iter: int) -> LUTtice:
        """Apply the chosen colour palette to a `Lattice`."""
        match self.palette_mode.value:
            case PaletteMode.PRESET.value:
                # default to "classic" palette if no stops are present
                lut = _interpolate_stops(PRESETS[self.chosen_preset], gamma=self.gamma)
            case PaletteMode.CUSTOM.value:
                lut = _interpolate_stops(
                    _extract_stops() or PRESETS["classic"],
                    gamma=self.gamma,
                )
            case _x:
                msg = f"unknown palette mode: {_x}"
                raise ValueError(msg)

        norm = np.clip(lat / Double(max_iter), Double(0.0), Double(1.0))
        idx = (norm * (len(lut) - 1)).astype(np.int32)
        rgb = lut[idx]  # .copy()
        inside = lat >= max_iter
        rgb[inside] = 0.0
        return (np.clip(rgb, 0.0, 1.0) * 255.0).astype(np.uint8)

    @override
    def build_dpg_params(self, parent: str, setattr_: WrappedSetattr) -> None:
        preset_creator_tag = "preset_creator"
        preset_combo_tag = "preset_combo"

        def _toggle_visibility(new_val: str) -> None:
            """Toggle the visibility of custom palette widgets."""
            setattr_(self, "palette_mode", PaletteMode(new_val))

            if new_val == PaletteMode.PRESET.value:
                dpg.hide_item(preset_creator_tag)
                dpg.show_item(preset_combo_tag)
            elif new_val == PaletteMode.CUSTOM.value:
                dpg.show_item(preset_creator_tag)
                dpg.hide_item(preset_combo_tag)
            else:
                msg = f"unknown palette mode: {new_val}"
                raise ValueError(msg)

        dpg.add_slider_float(
            label="gamma",
            default_value=self.gamma,
            no_input=True,
            min_value=0.01,
            max_value=1.0,
            format="%.2f",
            callback=lambda _, x: setattr_(self, "gamma", x),
            parent=parent,
        )
        dpg.add_combo(
            label="palette mode",
            items=[m.value for m in PaletteMode],
            default_value=PaletteMode.PRESET.value,
            callback=lambda _, x: _toggle_visibility(x),
            parent=parent,
        )
        dpg.add_combo(
            label="preset",
            tag=preset_combo_tag,
            items=list(PRESETS.keys()),
            default_value=next(iter(PRESETS.keys())),
            callback=lambda _, x: setattr_(self, "chosen_preset", x),
            parent=parent,
        )

        with dpg.child_window(
            tag=preset_creator_tag,
            border=False,
            show=False,
            auto_resize_y=True,
            parent=parent,
        ):
            dpg.add_separator()

            with dpg.group(tag=CUSTOM_COLOURS_GROUP_TAG):
                # just so it's anchored there
                pass

            for pos, c in CUSTOM_STOPS_DEFAULT:
                _add_stop(pos, c, should_redraw=False)

            dpg.add_button(
                label="add stop",
                callback=lambda: _add_stop(),
            )


def _add_stop(
    pos: float = 0.5,
    colour: Colour = (1.0, 1.0, 1.0),
    *,
    should_redraw: bool = True,
) -> None:
    """Add a new custom colour stop to the palette."""
    # dynamic import to bypass circular dependency
    from .daemons import redraw  # noqa: PLC0415

    with dpg.group(parent=CUSTOM_COLOURS_GROUP_TAG) as g:
        dpg.add_slider_float(
            label=f"t = {pos:.3f}",
            default_value=pos,
            width=180,
            min_value=0.0,
            max_value=1.0,
            callback=lambda s, a, _: lazy_chain(
                partial(
                    dpg.configure_item,
                    s,
                    label=f"t = {a:.3f}",
                ),
                redraw,
            )(),
        )
        dpg.add_color_picker(
            label="RGB",
            default_value=[
                int(colour[0] * 255),
                int(colour[1] * 255),
                int(colour[2] * 255),
                255,
            ],
            no_alpha=True,
            width=180,
            callback=lambda _s, _a, _u: redraw(),
        )
        dpg.add_button(
            label="delete",
            callback=lambda _s, _a, _u: lazy_chain(
                partial(dpg.delete_item, g),
                redraw,
            )(),
        )

    if should_redraw:
        redraw()


def _extract_stops() -> Preset:
    """Extract a list of custom colour stops from the UI state."""
    stops = []

    groups: list[int] = dpg.get_item_children(CUSTOM_COLOURS_GROUP_TAG, slot=1)  # type: ignore[reportAssignmentType]

    for g in groups:
        ch: list[int] = dpg.get_item_children(g, slot=1)  # type: ignore[reportAssignmentType]
        if len(ch) == 3:  # noqa: PLR2004
            slider = dpg.get_value(ch[0])
            rgb = dpg.get_value(ch[1])

            stops.append(
                (
                    # raw value
                    slider,
                    # everything but the alpha channel
                    (rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0),
                ),
            )

    return stops


def _interpolate_stops(stops: Preset, n: int = 2048, gamma: float = 1.0) -> np.ndarray:
    """Interpolate a list of custom colour stops into a continuous gradient."""
    n = max(2, n)
    t = np.linspace(0.0, 1.0, n, dtype=np.float32)
    out = np.zeros((n, 3), dtype=np.float32)

    stops = sorted(stops, key=lambda s: float(s[0]))
    if stops[0][0] > 0.0:
        stops = [(0.0, stops[0][1]), *stops]
    if stops[-1][0] < 1.0:
        stops = [*stops, (1.0, stops[-1][1])]

    for i in range(len(stops) - 1):
        t0, c0 = stops[i]
        t1, c1 = stops[i + 1]
        mask = (t >= t0) & (t <= t1)
        w = ((t[mask] - t0) / (t1 - t0))[:, None]
        c0 = np.array(c0, dtype=np.float32)
        c1 = np.array(c1, dtype=np.float32)
        out[mask] = (1.0 - w) * c0 + w * c1

    out = np.clip(out, 0.0, 1.0) ** (1.0 / gamma)

    return np.clip(out, 0.0, 1.0).astype(np.float32)
