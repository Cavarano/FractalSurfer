"""Implementation of Sierpinski's Triangle fractal."""

import random
from dataclasses import dataclass
from functools import lru_cache
from typing import override

import numpy as np
from dearpygui import dearpygui as dpg
from numba import jit

from common.camera import Camera
from common.reactive_params import ReactiveParams, WrappedSetattr
from common.types import Double, Lattice
from fractal.utils import Lat2D, n_zeros, rasterise_2d

from .base import FractalAlgorithm

VERTICES = np.array(
    [
        [0.0, 0.0],
        [1.0, 0.0],
        [0.5, np.sqrt(3) / 2.0],
    ],
    dtype=Double,
)


@dataclass
class SierpinskiParams(ReactiveParams):
    """Sierpinski's Triangle fractal parameters."""

    seed: int = 42
    num_points: int = 100_000

    @override
    def build_dpg_params(self, parent: str, setattr_: WrappedSetattr) -> None:
        dpg.add_slider_int(
            label="seed",
            no_input=True,
            min_value=0,
            max_value=1_000_000,
            default_value=self.seed,
            callback=lambda _, x: setattr_(self, "seed", int(x)),
            parent=parent,
        )
        dpg.add_slider_int(
            label="number of points",
            no_input=True,
            min_value=1000,
            max_value=10_000_000,
            default_value=self.num_points,
            callback=lambda _, x: setattr_(self, "num_points", int(x)),
            parent=parent,
        )


class SierpinskiAlgo(FractalAlgorithm[SierpinskiParams]):
    """Sierpinski's Triangle fractal algorithm (chaos game version)."""

    @override
    @staticmethod
    def default_camera(width: int, height: int) -> Camera:
        scale = Double(1.5 / min(width, height))

        return Camera(
            width=width,
            height=height,
            origin_x=width * scale / 5.5,
            origin_y=height * scale / 4,
            scale=scale,
        )

    @override
    @staticmethod
    def generate_frame(camera: Camera, params: SierpinskiParams) -> Lattice:
        pts = _cached_sierpinski_points(params.seed, params.num_points)
        return rasterise_2d(pts, camera)

    @staticmethod
    @jit(nopython=True)
    def _impl(
        seed: int,
        num_points: int,
    ) -> Lat2D:
        # numba PRNG, not CPython's
        random.seed(seed)

        v = VERTICES.copy()
        pts = n_zeros(num_points)

        x, y = np.mean(v[:, 0]), np.mean(v[:, 1])

        for i in range(num_points):
            k = random.randrange(len(v))  # noqa: S311
            vx, vy = v[k, 0], v[k, 1]
            x = (x + vx) * 0.5
            y = (y + vy) * 0.5
            pts[i, 0] = x
            pts[i, 1] = y

        return pts


@lru_cache(maxsize=10)
def _cached_sierpinski_points(seed: int, num_points: int) -> Lat2D:
    return SierpinskiAlgo._impl(seed, num_points)
