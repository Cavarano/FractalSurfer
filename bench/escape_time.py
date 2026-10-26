"""Per-frame timing for escape-time fractals (Mandelbrot, Julia, Burning Ship)."""

from __future__ import annotations

from dataclasses import dataclass

from bench import (
    _paths,  # noqa: F401  (sys.path setup)
    reporter,
)
from bench.cameras import escape_time_camera
from bench.timing import timeit
from fractal.burning_ship import BurningShipAlgo, BurningShipParams
from fractal.julia import JuliaAlgo, JuliaParams
from fractal.mandelbrot import MandelbrotAlgo, MandelbrotParams

# Cheapest first, so a `--quick` slice from the front is still informative.
_RESOLUTIONS = [(800, 600), (1200, 800), (1920, 1080)]
_MAX_ITERS = [100, 300, 1000]


@dataclass(frozen=True)
class EscapeTarget:
    name: str
    algo_cls: type
    params_cls: type


_TARGETS: list[EscapeTarget] = [
    EscapeTarget("Mandelbrot", MandelbrotAlgo, MandelbrotParams),
    EscapeTarget("Julia", JuliaAlgo, JuliaParams),
    EscapeTarget("Burning Ship", BurningShipAlgo, BurningShipParams),
]


def _measure_target(
    target: EscapeTarget,
    resolutions: list[tuple[int, int]],
    iters: list[int],
) -> list[list[float]]:
    """Return a 2D table of mean times: rows = resolutions, cols = iters."""
    rows: list[list[float]] = []
    for w, h in resolutions:
        cam = escape_time_camera(w, h)
        row: list[float] = []
        for mi in iters:
            params = target.params_cls(max_iter=mi)
            # Bind via default args to avoid late-binding closure capture
            t = timeit(
                lambda c=cam, p=params, a=target.algo_cls: a.generate_frame(c, p)
            )
            row.append(t)
        rows.append(row)
    return rows


def run(*, quick: bool = False) -> None:
    reporter.section(
        "Performance - escape-time fractals",
        "Mean time per frame in ms; n=5 measurements after one warmup.",
    )

    resolutions = _RESOLUTIONS[:-1] if quick else _RESOLUTIONS
    iters = _MAX_ITERS[:-1] if quick else _MAX_ITERS

    row_labels = [f"{w}x{h}" for w, h in resolutions]
    column_labels = [f"max_iter={mi}" for mi in iters]

    for target in _TARGETS:
        reporter.subsection(target.name)
        times = _measure_target(target, resolutions, iters)
        reporter.timing_table(row_labels, column_labels, times, row_header="Resolution")
        reporter.end_section()


if __name__ == "__main__":
    run()
