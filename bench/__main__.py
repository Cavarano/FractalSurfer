"""Command-line entry point.

Run from the repo root:

    uv run python -m bench               # full run
    uv run python -m bench --quick       # smaller grids
    uv run python -m bench --skip-jit    # skip the JIT first-call section
    uv run python -m bench --only ifs    # one section in isolation
"""

from __future__ import annotations

import argparse
import sys

from bench import correctness, escape_time, ifs, interpolation, jit

_SECTIONS = ("correctness", "escape", "ifs", "interpolation", "jit")


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="bench",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--quick", action="store_true", help="use smaller resolutions / point counts"
    )
    parser.add_argument(
        "--skip-jit",
        action="store_true",
        help="skip JIT first-call subprocess measurement",
    )
    parser.add_argument(
        "--only", choices=_SECTIONS, help="run a single section in isolation"
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)

    if args.only == "correctness":
        return 0 if correctness.run() else 1
    if args.only == "escape":
        escape_time.run(quick=args.quick)
        return 0
    if args.only == "ifs":
        ifs.run(quick=args.quick)
        return 0
    if args.only == "interpolation":
        return 0 if interpolation.run() else 1
    if args.only == "jit":
        jit.run()
        return 0

    # full run
    correctness_ok = correctness.run()
    interpolation_ok = interpolation.run()
    escape_time.run(quick=args.quick)
    ifs.run(quick=args.quick)
    if not args.skip_jit:
        jit.run()

    return 0 if correctness_ok and interpolation_ok else 1


if __name__ == "__main__":
    sys.exit(main())
