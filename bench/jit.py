"""First-call (JIT compilation) cost for Mandelbrot.

Numba's JIT cache lives in the dispatcher object and survives module reloads,
so the only reliable way to measure compilation cost is from a fresh
interpreter. This module spawns a subprocess to do exactly that.
"""

from __future__ import annotations

import subprocess
import sys
import textwrap

from bench import _paths, reporter

# What we run inside the subprocess. Kept as a string because it must execute
# in a clean interpreter that hasn't already imported Numba in this process.
_SUBPROCESS_SCRIPT = textwrap.dedent(
    """
    import sys, time
    sys.path.insert(0, {src!r})

    from common.camera import Camera
    from common.types import Double
    from fractal.mandelbrot import MandelbrotAlgo, MandelbrotParams

    w, h = 1200, 800
    s = Double(3.0 / min(w, h))
    cam = Camera(w, h, Double(w * s / 3), Double(h * s / 2), s)
    p = MandelbrotParams(max_iter=300)

    t0 = time.perf_counter()
    MandelbrotAlgo.generate_frame(cam, p)
    t_first = (time.perf_counter() - t0) * 1000

    t1 = time.perf_counter()
    MandelbrotAlgo.generate_frame(cam, p)
    t_warm = (time.perf_counter() - t1) * 1000

    print(f'{{t_first:.0f}} {{t_warm:.1f}}')
    """,
).strip()


def _measure() -> tuple[float, float]:
    """Run the subprocess and parse out (first_call_ms, warm_call_ms)."""
    code = _SUBPROCESS_SCRIPT.format(src=str(_paths.SRC))
    result = subprocess.run(  # noqa: S603
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        check=True,
    )
    t_first_str, t_warm_str = result.stdout.strip().split()
    return float(t_first_str), float(t_warm_str)


def run() -> None:
    reporter.section(
        "First-call cost (JIT compilation)",
        "Mandelbrot, 1200x800, max_iter=300. Measured in a fresh subprocess",
        "to avoid any prior Numba compiler state.",
    )

    t_first, t_warm = _measure()
    reporter.jit_summary(t_first, t_warm)
    reporter.end_section()


if __name__ == "__main__":
    run()
