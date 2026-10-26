"""Implementation of Barnsley's Fern fractal."""

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

from .base import FractalAlgorithm
from .utils import Lat2D, n_zeros, rasterise_2d

AffineRule = tuple[
    Double,
    Double,
    Double,
    Double,
    Double,
    Double,
    Double,
]


def _into(ftup: tuple) -> AffineRule:
    return tuple(map(Double, ftup))  # type: ignore[reportReturnType]


AFFINE_RULES: tuple[AffineRule, ...] = (
    _into((0.0, 0.0, 0.0, 0.16, 0.0, 0.0, 0.01)),
    _into((0.85, 0.04, -0.04, 0.85, 0.0, 1.60, 0.85)),
    _into((0.20, -0.26, 0.23, 0.22, 0.0, 1.60, 0.07)),
    _into((-0.15, 0.28, 0.26, 0.24, 0.0, 0.44, 0.07)),
)

CUMSUM = np.cumsum([r[6] for r in AFFINE_RULES])
CUMSUM /= CUMSUM[-1]


@dataclass
class FernParams(ReactiveParams):
    """Barnsley's Fern fractal parameters."""

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


class FernAlgo(FractalAlgorithm[FernParams]):
    """Barnsley's Fern fractal algorithm."""

    @override
    @staticmethod
    def default_camera(width: int, height: int) -> Camera:
        scale = Double(12 / min(width, height))

        return Camera(
            width=width,
            height=height,
            origin_x=width * scale / 2,
            origin_y=height * scale / 12,
            scale=scale,
        )

    @override
    @staticmethod
    def generate_frame(camera: Camera, params: FernParams) -> Lattice:
        pts = _cached_fern_points(
            params.seed,
            params.num_points,
        )
        return rasterise_2d(pts, camera)

    @staticmethod
    @jit(nopython=True)
    def _impl(seed: int, num_points: int, rules: tuple[AffineRule, ...]) -> Lat2D:
        # numba PRNG, not CPython's
        random.seed(seed)

        pts = n_zeros(num_points)
        x, y = Double(0), Double(0)

        for i in range(num_points):
            r = random.random()  # noqa: S311
            idx = np.searchsorted(CUMSUM, r, side="left")
            rule = rules[idx]

            x_new = rule[0] * x + rule[1] * y + rule[4]
            y_new = rule[2] * x + rule[3] * y + rule[5]
            x, y = x_new, y_new
            pts[i, 0] = x
            pts[i, 1] = y

        return pts


@lru_cache(maxsize=10)
def _cached_fern_points(seed: int, num_points: int) -> Lat2D:
    return FernAlgo._impl(seed, num_points, rules=AFFINE_RULES)
