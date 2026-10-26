"""Implementation of the Mandelbrot fractal."""

from dataclasses import dataclass
from typing import override

import numpy as np
from dearpygui import dearpygui as dpg
from numba import jit

from common.camera import Camera
from common.reactive_params import ReactiveParams, WrappedSetattr
from common.types import Double, Lattice

from .base import FractalAlgorithm

RADIUS = Double(2.0)
ESCAPE_BOUND = Double(np.pow(RADIUS, 2))


@dataclass
class MandelbrotParams(ReactiveParams):
    """Mandelbrot fractal parameters."""

    max_iter: int = 300

    @override
    def build_dpg_params(self, parent: str, setattr_: WrappedSetattr) -> None:
        dpg.add_slider_int(
            label="max iterations",
            no_input=True,
            min_value=1,
            max_value=1000,
            default_value=self.max_iter,
            callback=lambda _, x: setattr_(self, "max_iter", int(x)),
            parent=parent,
        )


class MandelbrotAlgo(FractalAlgorithm[MandelbrotParams]):
    """Mandelbrot fractal algorithm."""

    @override
    @staticmethod
    def default_camera(width: int, height: int) -> Camera:
        scale = Double(3 / min(width, height))

        return Camera(
            width=width,
            height=height,
            origin_x=width * scale / 3,
            origin_y=height * scale / 2,
            scale=scale,
        )

    @override
    @staticmethod
    def generate_frame(camera: Camera, params: MandelbrotParams) -> Lattice:
        return MandelbrotAlgo._impl(
            camera.width,
            camera.height,
            camera.origin_x,
            camera.origin_y,
            camera.scale,
            params.max_iter,
        )

    @staticmethod
    @jit(nopython=True)
    def _impl(  # noqa: PLR0913
        width: int,
        height: int,
        ox: Double,
        oy: Double,
        scale: Double,
        max_iter: int,
    ) -> Lattice:
        esc_lat = np.zeros((height, width), dtype=Double)

        for y in range(height):
            for x in range(width):
                x0 = (x - width) * scale + ox  # c.re
                y0 = (y - height) * scale + oy  # c.im
                zx = Double(0.0)  # z_0 = 0
                zy = Double(0.0)

                it = 0
                while it < max_iter and (zx * zx + zy * zy) <= ESCAPE_BOUND:
                    zx, zy = zx * zx - zy * zy + x0, 2.0 * zx * zy + y0
                    it += 1

                if it < max_iter:
                    # smooth coloring
                    r = np.sqrt(zx * zx + zy * zy)
                    mu = it - np.log(np.log(r)) / np.log(2.0)

                    esc_lat[y, x] = Double(mu)
                else:
                    esc_lat[y, x] = Double(max_iter)

        return esc_lat
