"""Implementation of the Julia fractal."""

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
class JuliaParams(ReactiveParams):
    """Julia fractal parameters."""

    max_iter: int = 300
    mandelbrot_const_re: Double = Double(-0.8)  # noqa: RUF009
    mandelbrot_const_im: Double = Double(0.156)  # noqa: RUF009

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
        dpg.add_slider_double(
            label="c.re",
            no_input=True,
            min_value=-2.0,
            max_value=2.0,
            default_value=float(self.mandelbrot_const_re),
            callback=lambda _, x: setattr_(self, "mandelbrot_const_re", Double(x)),
            parent=parent,
        )
        dpg.add_slider_double(
            label="c.im",
            no_input=True,
            min_value=-2.0,
            max_value=2.0,
            default_value=float(self.mandelbrot_const_im),
            callback=lambda _, x: setattr_(self, "mandelbrot_const_im", Double(x)),
            parent=parent,
        )


class JuliaAlgo(FractalAlgorithm[JuliaParams]):
    """Mandelbrot fractal algorithm."""

    @override
    @staticmethod
    def default_camera(width: int, height: int) -> Camera:
        scale = Double(3.5 / min(width, height))

        return Camera(
            width=width,
            height=height,
            origin_x=width * scale / 2,
            origin_y=height * scale / 2,
            scale=scale,
        )

    @override
    @staticmethod
    def generate_frame(camera: Camera, params: JuliaParams) -> Lattice:
        return JuliaAlgo._impl(
            camera.width,
            camera.height,
            camera.origin_x,
            camera.origin_y,
            params.mandelbrot_const_re,
            params.mandelbrot_const_im,
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
        c_re: Double,
        c_im: Double,
        scale: Double,
        max_iter: int,
    ) -> Lattice:
        esc_lat = np.zeros((height, width), dtype=Double)

        for y in range(height):
            for x in range(width):
                zx = (x - width) * scale + ox
                zy = (y - height) * scale + oy

                it = 0
                while it < max_iter and (zx * zx + zy * zy) <= ESCAPE_BOUND:
                    zx, zy = zx * zx - zy * zy + c_re, 2.0 * zx * zy + c_im
                    it += 1

                if it < max_iter:
                    # smooth coloring
                    r = np.sqrt(zx * zx + zy * zy)
                    mu = it - np.log(np.log(r)) / np.log(2.0)

                    esc_lat[y, x] = Double(mu)
                else:
                    esc_lat[y, x] = Double(max_iter)

        return esc_lat
