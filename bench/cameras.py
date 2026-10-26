"""Camera construction helpers for benchmark scenarios."""

from __future__ import annotations

from bench import _paths  # noqa: F401  (sys.path setup)
from common.camera import Camera
from common.types import Double


def escape_time_camera(width: int, height: int) -> Camera:
    """A reasonable default camera for benchmarking escape-time fractals.

    The framing is similar to `MandelbrotAlgo.default_camera` but kept
    independent so that benchmark numbers don't shift if the production
    default changes.
    """
    s = Double(3.0 / min(width, height))
    return Camera(
        width=width,
        height=height,
        origin_x=Double(width * s / 3),
        origin_y=Double(height * s / 2),
        scale=s,
    )


def single_pixel_probe(c_re: float, c_im: float) -> Camera:
    """A 1x1 camera that samples exactly the complex point (c_re, c_im).

    Background: the camera anchors `(origin_x, origin_y)` to the bottom-right
    pixel; for a 1x1 camera the only sample is at `(x, y) = (0, 0)`, so the
    complex value evaluated by the fractal is `(0 - 1) * scale + origin_x`.
    Setting `origin_x = c_re + scale` makes that work out to exactly `c_re`.
    """
    scale = Double(1e-12)
    return Camera(
        width=1,
        height=1,
        origin_x=Double(c_re) + scale,
        origin_y=Double(c_im) + scale,
        scale=scale,
    )
