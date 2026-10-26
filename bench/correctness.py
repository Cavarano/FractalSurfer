"""Sanity-checks Mandelbrot membership at known points.

Not a full test suite - just enough to catch a regression that would change
the visual output of the program. Boundary points (cardioid cusp, period-2
bifurcation) are reported but not asserted, since their classification
depends on `max_iter` and is not robust.
"""

from __future__ import annotations

from bench import (
    _paths,  # noqa: F401  (sys.path setup)
    reporter,
)
from bench.cameras import single_pixel_probe
from bench.reporter import CheckResult, InfoResult
from common.types import Double
from fractal.mandelbrot import MandelbrotAlgo, MandelbrotParams

DEFAULT_MAX_ITER = 500


def probe_mandelbrot(
    c_re: float, c_im: float, *, max_iter: int = DEFAULT_MAX_ITER
) -> Double:
    """Return the Mandelbrot iteration value at a single complex point `c`."""
    cam = single_pixel_probe(c_re, c_im)
    lat = MandelbrotAlgo.generate_frame(cam, MandelbrotParams(max_iter=max_iter))
    return lat[0, 0]


# (c_re, c_im, expected_inside, description)
_ASSERTED_CASES: list[tuple[float, float, bool, str]] = [
    (0.0, 0.0, True, "c=0: heart of the set"),
    (-1.0, 0.0, True, "c=-1: period-2 orbit"),
    (-0.5, 0.0, True, "c=-0.5: inside main cardioid"),
    (3.0, 0.0, False, "c=3: far outside"),
    (0.5, 0.5, False, "c=0.5+0.5i: outside"),
    (-2.5, 0.0, False, "c=-2.5: outside, on the real axis"),
]

# (c_re, c_im, description) - informational only, not checked
_BOUNDARY_CASES: list[tuple[float, float, str]] = [
    (0.25, 0.0, "c=0.25: main cardioid cusp"),
    (-0.75, 0.0, "c=-0.75: period-2 bifurcation point"),
]


def run() -> bool:
    """Run all checks. Returns True iff every asserted case passed."""
    reporter.section("Correctness - Mandelbrot point membership")

    # warm up JIT once with a tiny call
    probe_mandelbrot(0.0, 0.0, max_iter=10)

    asserted: list[CheckResult] = []
    for c_re, c_im, expected_inside, desc in _ASSERTED_CASES:
        val = probe_mandelbrot(c_re, c_im)
        actually_inside = val >= DEFAULT_MAX_ITER
        asserted.append(
            CheckResult(
                description=desc,
                value=float(val),
                passed=actually_inside == expected_inside,
            ),
        )

    informational: list[InfoResult] = [
        InfoResult(description=desc, value=float(probe_mandelbrot(c_re, c_im)))
        for c_re, c_im, desc in _BOUNDARY_CASES
    ]

    reporter.correctness_results(asserted, informational)
    reporter.end_section()

    return all(r.passed for r in asserted)


if __name__ == "__main__":
    import sys

    sys.exit(0 if run() else 1)
