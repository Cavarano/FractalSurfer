"""Utility functions used throughout the UI code."""

from collections.abc import Callable
from functools import cache
from inspect import signature

import numpy as np

from common.types import Lattice


def lazy_chain(*funcs: Callable[[], None]) -> Callable[[], None]:
    """Compose a list of functions into a single function."""

    def _inner() -> None:
        for func in funcs:
            func()

    return _inner


@cache
def has_member(cls: type, member: str) -> bool:
    """Check if a class has a member with the given name."""
    return member in signature(obj=cls).parameters


def upscale_lat(
    small_lat: Lattice,
    downscale_factor: int,
    width: int,
    height: int,
) -> Lattice:
    """Upscale a lattice to the given dimensions."""
    lattice = np.repeat(
        np.repeat(small_lat, downscale_factor, axis=0),
        downscale_factor,
        axis=1,
    )

    # if the upscaled lattice is too small, repeat the last row/column as needed
    h, w = lattice.shape
    if h < height:
        last_row = lattice[-1:, :]
        reps = height - h
        lattice = np.concatenate([lattice, np.repeat(last_row, reps, axis=0)], axis=0)
    if w < width:
        last_col = lattice[:, -1:]
        reps = width - w
        lattice = np.concatenate([lattice, np.repeat(last_col, reps, axis=1)], axis=1)

    return lattice[:height, :width]
