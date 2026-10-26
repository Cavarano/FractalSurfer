"""Tiny timing helper used across benchmark sections."""

from __future__ import annotations

import time
from collections.abc import Callable


def timeit(fn: Callable[[], object], *, warmup: int = 1, n: int = 5) -> float:
    """Return mean wall-clock time in milliseconds.

    Runs `fn` `warmup` times first to absorb one-off costs (JIT compilation,
    cache priming), then `n` more times for the actual measurement.
    """
    for _ in range(warmup):
        fn()

    times: list[float] = []
    for _ in range(n):
        t0 = time.perf_counter()
        fn()
        times.append((time.perf_counter() - t0) * 1000)

    return sum(times) / len(times)
