"""Common utilities related to camera manipulation."""
# ruff: noqa: SLF001

import math
from collections.abc import Collection
from dataclasses import dataclass, replace
from enum import Enum
from typing import Self, override

from dearpygui import dearpygui as dpg

from .reactive_params import ReactiveParams, WrappedSetattr
from .types import Double

_CAMERA_COORDS_TAG = "camera_coords"


class Key(Enum):
    """Keys that can be used to control a `Camera`."""

    UP = dpg.mvKey_W
    DOWN = dpg.mvKey_S
    LEFT = dpg.mvKey_A
    RIGHT = dpg.mvKey_D
    ZOOM_IN = dpg.mvKey_Q
    ZOOM_OUT = dpg.mvKey_E


@dataclass
class CameraParams(ReactiveParams):
    """Parameters used to control camera movements."""

    movement_enabled_downscaling: bool = False
    user_enabled_downscaling: bool = True
    polling_stagger: float = 0.1
    shift_mod: Double = Double(1.5)  # noqa: RUF009
    ctrl_mod: Double = Double(0.5)  # noqa: RUF009
    move_speed: int = 15
    zoom_speed: Double = Double(0.95)  # noqa: RUF009
    downscale_factor: int = 2
    iteration_limit: int = 300

    @override
    def build_dpg_params(self, parent: str, setattr_: WrappedSetattr) -> None:
        dpg.add_text("center coords: N/A", tag=_CAMERA_COORDS_TAG)

        dpg.add_checkbox(
            label="movement downscaling (if applicable)",
            default_value=self.user_enabled_downscaling,
            callback=lambda _, x: setattr_(self, "user_enabled_downscaling", x),
            parent=parent,
        )
        dpg.add_slider_int(
            label="downscale factor",
            default_value=self.downscale_factor,
            no_input=True,
            min_value=2,
            max_value=16,
            callback=lambda _, x: setattr_(self, "downscale_factor", x),
            parent=parent,
        )
        dpg.add_slider_int(
            label="iteration limit",
            default_value=self.iteration_limit,
            no_input=True,
            min_value=1,
            max_value=1000,
            callback=lambda _, x: setattr_(self, "iteration_limit", x),
            parent=parent,
        )
        dpg.add_slider_int(
            label="movement speed",
            default_value=self.move_speed,
            no_input=True,
            min_value=1,
            max_value=50,
            callback=lambda _, x: setattr_(self, "move_speed", x),
            parent=parent,
        )
        dpg.add_slider_double(
            label="zoom speed",
            default_value=float(1 - self.zoom_speed),
            no_input=True,
            min_value=0.01,
            max_value=0.10,
            format="%.2f",
            callback=lambda _, x: setattr_(self, "zoom_speed", Double(1 - x)),
            parent=parent,
        )
        dpg.add_slider_double(
            label="Shift speed modifier",
            default_value=float(self.shift_mod),
            no_input=True,
            min_value=1.0,
            max_value=2.0,
            format="%.2f",
            callback=lambda _, x: setattr_(self, "shift_mod", Double(x)),
            parent=parent,
        )
        dpg.add_slider_double(
            label="Ctrl speed modifier",
            default_value=float(self.ctrl_mod),
            no_input=True,
            min_value=0.1,
            max_value=1.0,
            format="%.2f",
            callback=lambda _, x: setattr_(self, "ctrl_mod", Double(x)),
            parent=parent,
        )
        dpg.add_slider_double(
            label="polling stagger",
            default_value=self.polling_stagger,
            no_input=True,
            min_value=0.01,
            max_value=0.2,
            callback=lambda _, x: setattr_(self, "polling_stagger", float(x)),
            parent=parent,
        )


@dataclass
class Camera:
    """A view of a fractal slice."""

    width: int
    height: int
    origin_x: Double
    origin_y: Double
    scale: Double

    def _move_left(self, move_speed: int) -> Self:
        return replace(self, origin_x=self.origin_x - self.scale * move_speed)

    def _move_right(self, move_speed: int) -> Self:
        return replace(self, origin_x=self.origin_x + self.scale * move_speed)

    def _move_up(self, move_speed: int) -> Self:
        return replace(self, origin_y=self.origin_y - self.scale * move_speed)

    def _move_down(self, move_speed: int) -> Self:
        return replace(self, origin_y=self.origin_y + self.scale * move_speed)

    def center_xy(self) -> tuple[Double, Double]:
        """Return the center coordinates of the camera."""
        return (
            self.origin_x - self.width * self.scale / 2,
            self.origin_y - self.height * self.scale / 2,
        )

    def _zoom(self, zoom_speed: Double) -> Self:
        cx, cy = self.center_xy()
        new_scale = self.scale * zoom_speed
        # preserve centre: new_ox = cx + W*new_s/2
        return replace(
            self,
            scale=new_scale,
            origin_x=Double(cx + self.width * new_scale / 2),
            origin_y=Double(cy + self.height * new_scale / 2),
        )

    def apply_movements(  # noqa: C901
        self,
        keys: Collection[Key],
        params: CameraParams,
    ) -> Self:
        """Apply a set of movements to the camera."""
        temp = self

        shift_down = dpg.is_key_down(
            dpg.mvKey_LShift,
        ) or dpg.is_key_down(
            dpg.mvKey_RShift,
        )
        ctrl_down = dpg.is_key_down(
            dpg.mvKey_LControl,
        ) or dpg.is_key_down(
            dpg.mvKey_RControl,
        )

        match (shift_down, ctrl_down):
            case True, True:
                mod = Double(1.0)
            case True, False:
                mod = params.shift_mod
            case False, True:
                mod = params.ctrl_mod
            case False, False:
                mod = Double(1.0)

        mod_move_speed = int(params.move_speed * mod)
        mod_zoom_speed = Double(params.zoom_speed**mod)

        if Key.UP in keys and Key.DOWN not in keys:
            temp = temp._move_up(mod_move_speed)
        elif Key.DOWN in keys and Key.UP not in keys:
            temp = temp._move_down(mod_move_speed)

        if Key.LEFT in keys and Key.RIGHT not in keys:
            temp = temp._move_left(mod_move_speed)
        elif Key.RIGHT in keys and Key.LEFT not in keys:
            temp = temp._move_right(mod_move_speed)

        if Key.ZOOM_IN in keys and Key.ZOOM_OUT not in keys:
            temp = temp._zoom(mod_zoom_speed)
        elif Key.ZOOM_OUT in keys and Key.ZOOM_IN not in keys:
            temp = temp._zoom(1 / mod_zoom_speed)

        center = temp.center_xy()

        # update camera coordinates label
        dpg.set_value(
            _CAMERA_COORDS_TAG,
            f"center coords: ({center[0]:.5f}, {center[1]:.5f})",
        )

        return temp


def interpolate_linear(cams: list[Camera], num: int) -> list[Camera]:
    """Interpolate linearly between each pair of Camera objects."""
    if len(cams) < 2 or num < 2:  # noqa: PLR2004
        # not enough cameras or steps to interpolate
        return cams

    result = []
    for i in range(len(cams) - 1):
        cam_start = cams[i]
        cam_end = cams[i + 1]
        # compute centers (origin is top-left corner, we need to interpolate centers)
        center_start = cam_start.center_xy()
        center_end = cam_end.center_xy()
        # interpolate scale in log-space for smooth exponential zoom
        log_scale_start = math.log(cam_start.scale)
        log_scale_end = math.log(cam_end.scale)
        for j in range(num):
            t = j / (num - 1) if num > 1 else 0.0
            scale = Double(math.exp(log_scale_start * (1 - t) + log_scale_end * t))
            # interpolate center proportionally to scale for visually straight path
            # when scales are equal, fall back to linear interpolation (s = 1 - t)
            if math.isclose(cam_start.scale, cam_end.scale):
                s = 1 - t
            else:
                s = (scale - cam_end.scale) / (cam_start.scale - cam_end.scale)
            center_x = center_start[0] * s + center_end[0] * (1 - s)
            center_y = center_start[1] * s + center_end[1] * (1 - s)
            # derive origin from center and scale
            interp = Camera(
                width=cam_start.width,
                height=cam_start.height,
                origin_x=Double(center_x + cam_start.width * scale / 2),
                origin_y=Double(center_y + cam_start.height * scale / 2),
                scale=scale,
            )
            result.append(interp)
    return result


def interpolate_catmull_rom(cams: list[Camera], num: int) -> list[Camera]:
    """Interpolate Camera parameters using Catmull-Rom splines."""
    if len(cams) < 2 or num < 2:  # noqa: PLR2004
        # not enough cameras or steps to interpolate
        return cams

    def _catmull_rom(
        p0: float,
        p1: float,
        p2: float,
        p3: float,
        t: float,
    ) -> float:
        return 0.5 * (
            2 * p1
            + (p2 - p0) * t
            + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t**2
            + (3 * p1 - p0 - 3 * p2 + p3) * t**3
        )

    # spline the centre + log(scale); origin is coupled to scale so splining it
    # directly entangles position with zoom and warps the path
    centres = [c.center_xy() for c in cams]
    log_scales = [math.log(c.scale) for c in cams]

    def _reflect(a: float, b: float) -> float:
        return 2 * b - a

    cx = [float(p[0]) for p in centres]
    cy = [float(p[1]) for p in centres]
    ls = [float(s) for s in log_scales]

    # reflected phantom points at boundaries to avoid oscillation
    cx_pre = _reflect(cx[1], cx[0])
    cy_pre = _reflect(cy[1], cy[0])
    ls_pre = _reflect(ls[1], ls[0])
    cx_post = _reflect(cx[-2], cx[-1])
    cy_post = _reflect(cy[-2], cy[-1])
    ls_post = _reflect(ls[-2], ls[-1])

    result = []
    n = len(cams)
    for i in range(n - 1):
        cx0 = cx[i - 1] if i > 0 else cx_pre
        cy0 = cy[i - 1] if i > 0 else cy_pre
        ls0 = ls[i - 1] if i > 0 else ls_pre
        cx1, cy1, ls1 = cx[i], cy[i], ls[i]
        cx2, cy2, ls2 = cx[i + 1], cy[i + 1], ls[i + 1]
        cx3 = cx[i + 2] if i + 2 < n else cx_post
        cy3 = cy[i + 2] if i + 2 < n else cy_post
        ls3 = ls[i + 2] if i + 2 < n else ls_post

        p1 = cams[i]
        for j in range(num):
            t = j / (num - 1) if num > 1 else 0.0
            centre_x = _catmull_rom(cx0, cx1, cx2, cx3, t)
            centre_y = _catmull_rom(cy0, cy1, cy2, cy3, t)
            scale = Double(math.exp(_catmull_rom(ls0, ls1, ls2, ls3, t)))
            result.append(
                Camera(
                    width=p1.width,
                    height=p1.height,
                    origin_x=Double(centre_x + p1.width * scale / 2),
                    origin_y=Double(centre_y + p1.height * scale / 2),
                    scale=scale,
                ),
            )

    return result
