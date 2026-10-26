"""Output formatting for benchmark sections.

All `print` calls live here. Section modules describe results structurally;
the reporter owns headers, tables, status markers, and spacing.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CheckResult:
    """A single asserted correctness check."""

    description: str
    value: float
    passed: bool


@dataclass(frozen=True)
class InfoResult:
    """A single informational (unasserted) measurement."""

    description: str
    value: float


def section(title: str, *subtitle_lines: str) -> None:
    """Print a top-level section header with optional explanatory lines."""
    print(f"=== {title} ===")
    for line in subtitle_lines:
        print(line)
    if subtitle_lines:
        print()


def subsection(title: str) -> None:
    """Print a subsection header for one target within a section."""
    print(f"--- {title} ---")


def end_section() -> None:
    """Trailing blank line after a section, for spacing."""
    print()


def correctness_results(
    asserted: list[CheckResult],
    informational: list[InfoResult],
) -> None:
    """Render correctness check output."""
    for r in asserted:
        marker = "OK  " if r.passed else "FAIL"
        print(f"  [{marker}] {r.description:<45}  val = {r.value:.2f}")

    if informational:
        print("\n  (boundary points - informational only, not checked)")
        for r in informational:
            print(f"        {r.description:<45}  val = {r.value:.2f}")


def timing_table(
    row_labels: list[str],
    column_labels: list[str],
    times_ms: list[list[float]],
    *,
    row_header: str = "",
) -> None:
    """Render a 2D timing table.

    `times_ms[i][j]` is the time for `row_labels[i]` x `column_labels[j]`.
    """
    print(f"{row_header:<16}" + "".join(f"  {label:>14}" for label in column_labels))
    for label, row in zip(row_labels, times_ms, strict=True):
        cells = "".join(f"  {t:>11.1f} ms" for t in row)
        print(f"{label:<16}{cells}")


def timing_list(measurements: list[tuple[str, float]]) -> None:
    """Render a flat list of (label, time_ms) measurements."""
    for label, t in measurements:
        print(f"  {label:>14}  ->  {t:>8.1f} ms")


def jit_summary(t_first_ms: float, t_warm_ms: float) -> None:
    """Render the JIT first-call vs. warm-call comparison."""
    print(f"  First call:           {t_first_ms:>8.0f} ms  (compilation + computation)")
    print(f"  Subsequent call:      {t_warm_ms:>8.1f} ms  (computation only)")
    print(f"  Compilation overhead: {t_first_ms - t_warm_ms:>8.0f} ms  (difference)")
