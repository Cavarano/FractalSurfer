"""Sanity-checks for camera keyframe interpolation.

Camera state mixes a position (centre) with an exponential zoom (scale),
and `origin` is coupled to both via `origin = centre + size * scale / 2`.
Splining `origin` directly therefore entangles position with zoom, so the
interpolators are required to spline centre + log(scale) and reconstruct
origin. These checks pin down that contract.
"""

from __future__ import annotations

from bench import (
    _paths,  # noqa: F401  (sys.path setup)
    reporter,
)
from bench.reporter import CheckResult
from common.camera import Camera, interpolate_catmull_rom, interpolate_linear
from common.types import Double

_WIDTH, _HEIGHT = 800, 600
_SHARED_CENTRE = (Double(0.123), Double(-0.456))
_CENTRE_TOL = 1e-9
_ENDPOINT_TOL = 1e-9


def _cam(centre: tuple[Double, Double], scale: Double) -> Camera:
    return Camera(
        width=_WIDTH,
        height=_HEIGHT,
        origin_x=Double(centre[0] + _WIDTH * scale / 2),
        origin_y=Double(centre[1] + _HEIGHT * scale / 2),
        scale=scale,
    )


def _max_centre_drift(frames: list[Camera], target: tuple[Double, Double]) -> float:
    return float(
        max(
            max(abs(f.center_xy()[0] - target[0]), abs(f.center_xy()[1] - target[1]))
            for f in frames
        ),
    )


def _frame_error(frame: Camera, expected: Camera) -> float:
    fx, fy = frame.center_xy()
    ex, ey = expected.center_xy()
    return float(
        max(
            abs(fx - ex),
            abs(fy - ey),
            abs(float(frame.scale) - float(expected.scale)),
        ),
    )


def run() -> bool:
    """Run all interpolation checks. Returns True iff every case passed."""
    reporter.section("Correctness - Camera keyframe interpolation")

    # shared centre, very different scale: every interpolated frame must
    # land on the shared centre; splining origin directly fails this because
    # origin = centre + W*scale/2 drifts with scale
    a = _cam(_SHARED_CENTRE, Double(1e-2))
    b = _cam(_SHARED_CENTRE, Double(1e-6))

    lin_shared = interpolate_linear([a, b], 20)
    cr_shared = interpolate_catmull_rom([a, b], 20)

    # endpoints of the interpolated sequence must coincide with the keyframes,
    # in centre and scale; the y-sign flip in linear breaks this
    p = _cam((Double(0.5), Double(1.5)), Double(0.01))
    q = _cam((Double(2.0), Double(-1.0)), Double(0.001))
    lin_pq = interpolate_linear([p, q], 10)
    cr_pq = interpolate_catmull_rom([p, q], 10)

    # 3 keyframes: each segment boundary must hit the corresponding keyframe
    r = _cam((Double(-0.7), Double(0.3)), Double(0.0001))
    cr_pqr = interpolate_catmull_rom([p, q, r], 8)

    cases = [
        CheckResult(
            description="linear: shared-centre frames stay on centre",
            value=_max_centre_drift(lin_shared, _SHARED_CENTRE),
            passed=_max_centre_drift(lin_shared, _SHARED_CENTRE) < _CENTRE_TOL,
        ),
        CheckResult(
            description="catmull-rom: shared-centre frames stay on centre",
            value=_max_centre_drift(cr_shared, _SHARED_CENTRE),
            passed=_max_centre_drift(cr_shared, _SHARED_CENTRE) < _CENTRE_TOL,
        ),
        CheckResult(
            description="linear: endpoints match keyframes",
            value=max(_frame_error(lin_pq[0], p), _frame_error(lin_pq[-1], q)),
            passed=max(_frame_error(lin_pq[0], p), _frame_error(lin_pq[-1], q))
            < _ENDPOINT_TOL,
        ),
        CheckResult(
            description="catmull-rom: endpoints match keyframes",
            value=max(_frame_error(cr_pq[0], p), _frame_error(cr_pq[-1], q)),
            passed=max(_frame_error(cr_pq[0], p), _frame_error(cr_pq[-1], q))
            < _ENDPOINT_TOL,
        ),
        CheckResult(
            description="catmull-rom: 3-keyframe segment boundaries are exact",
            value=max(
                _frame_error(cr_pqr[0], p),
                _frame_error(cr_pqr[8], q),
                _frame_error(cr_pqr[-1], r),
            ),
            passed=max(
                _frame_error(cr_pqr[0], p),
                _frame_error(cr_pqr[8], q),
                _frame_error(cr_pqr[-1], r),
            )
            < _ENDPOINT_TOL,
        ),
    ]

    reporter.correctness_results(cases, [])
    reporter.end_section()

    return all(r.passed for r in cases)


if __name__ == "__main__":
    import sys

    sys.exit(0 if run() else 1)
