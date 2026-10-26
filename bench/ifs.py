"""Per-frame timing for point-based (IFS) fractals - Sierpinski and Fern.

The IFS algorithms cache their point clouds on `_impl` via `@lru_cache`.
To benchmark genuine generation cost, every measured call uses a fresh seed
*and* clears the cache, ensuring no measurement hits a cached result.
"""

from __future__ import annotations

from dataclasses import dataclass

from bench import (
    _paths,  # noqa: F401  (sys.path setup)
    reporter,
)
from bench.timing import timeit
from fractal.fern import FernAlgo, FernParams
from fractal.sierpinski import SierpinskiAlgo, SierpinskiParams

_POINT_COUNTS = [10_000, 100_000, 1_000_000, 5_000_000]
_BENCH_RESOLUTION = (1200, 800)


@dataclass(frozen=True)
class IFSTarget:
    name: str
    algo_cls: type
    params_cls: type


_TARGETS: list[IFSTarget] = [
    IFSTarget("Sierpinski", SierpinskiAlgo, SierpinskiParams),
    IFSTarget("Barnsley's Fern", FernAlgo, FernParams),
]


from fractal.fern import _cached_fern_points
from fractal.sierpinski import _cached_sierpinski_points

# Map each algo to its module-level cached wrapper.
_CACHED_FOR: dict[type, object] = {
    SierpinskiAlgo: _cached_sierpinski_points,
    FernAlgo: _cached_fern_points,
}


def _measure_target(
    target: IFSTarget, point_counts: list[int]
) -> list[tuple[str, float]]:
    """Return a list of (label, time_ms) rows, one per point count."""
    w, h = _BENCH_RESOLUTION
    cam = target.algo_cls.default_camera(w, h)
    cached = _CACHED_FOR[target.algo_cls]
    counter = [0]

    def call_for(n: int) -> None:
        counter[0] += 1
        params = target.params_cls(num_points=n, seed=counter[0])
        cached.cache_clear()
        target.algo_cls.generate_frame(cam, params)

    rows: list[tuple[str, float]] = []
    for n in point_counts:
        t = timeit(lambda nn=n: call_for(nn), warmup=1, n=3)
        rows.append((f"{n:,} pts", t))
    return rows


def run(*, quick: bool = False) -> None:
    reporter.section("Performance - IFS fractals (point cloud + rasterisation)")

    point_counts = _POINT_COUNTS[:-1] if quick else _POINT_COUNTS

    for target in _TARGETS:
        reporter.subsection(target.name)
        rows = _measure_target(target, point_counts)
        reporter.timing_list(rows)
        reporter.end_section()


if __name__ == "__main__":
    run()
