"""Fractal generation utilities."""

import numpy as np
from numba import jit

from common.camera import Camera
from common.types import Double, Lattice

Lat2D = np.ndarray[tuple[int, 2], np.dtype[Double]]
"""
An array of 2D points.
"""


@jit(nopython=True)
def n_zeros(num_points: int) -> Lat2D:
    """Return an empty array of shape (num_points, 2)."""
    return np.zeros((num_points, 2), dtype=Double)  # type: ignore[reportAssignmentType]


def rasterise_2d(pts: Lat2D, camera: Camera, *, flip: bool = True) -> Lattice:
    """Rasterise a set of 2D points into a `Lattice`, matching the camera's view."""
    lattice = np.zeros((camera.height, camera.width), dtype=Double)

    # map points to pixel indices
    x_pix = ((pts[:, 0] + camera.origin_x) / camera.scale).astype(int)
    y_pix = ((pts[:, 1] + camera.origin_y) / camera.scale).astype(int)

    # filter points inside the view
    mask = (
        (x_pix >= 0) & (x_pix < camera.width) & (y_pix >= 0) & (y_pix < camera.height)
    )
    x_pix = x_pix[mask]
    y_pix = y_pix[mask]

    # set lattice at valid pixel locations to their index
    idxs = np.arange(pts.shape[0])[mask]
    lattice[y_pix, x_pix] = idxs

    # flip horizontally and vertically if asked to
    if flip is True:
        return np.flipud(np.fliplr(lattice))
    else:  # noqa: RET505
        return lattice
