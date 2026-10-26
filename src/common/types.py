"""Common types used throughouit the project."""

import numpy as np

Double = np.double
"""
Double precision floating point number.
`np.double` is used for consistency, as built-in floats can be problematic.
"""

Lattice = np.ndarray[tuple[int, int], np.dtype[Double]]
"""
Two-dimensional array of `Double`s.
"""

LUTtice = np.ndarray[tuple[int, int, 3], np.dtype[np.uint8]]
"""
Three-dimensional array of `np.uint8`s - a `Lattice` with LUT applied for color mapping.
"""
