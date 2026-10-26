"""Fractal algorithm choice & param utilities."""

from enum import Enum
from typing import Self

from common.reactive_params import ReactiveParams
from fractal.base import FractalAlgorithm
from fractal.burning_ship import (
    BurningShipAlgo,
    BurningShipParams,
)
from fractal.fern import (
    FernAlgo,
    FernParams,
)
from fractal.julia import (
    JuliaAlgo,
    JuliaParams,
)
from fractal.mandelbrot import (
    MandelbrotAlgo,
    MandelbrotParams,
)
from fractal.sierpinski import (
    SierpinskiAlgo,
    SierpinskiParams,
)


class AlgoChoice(Enum):
    """Chosen fractal generation algorithm."""

    MANDELBROT = "Mandelbrot"
    JULIA = "Julia"
    FERN = "Fern"
    SIERPINSKI = "Sierpinski"
    BURNING_SHIP = "Burning Ship"

    @classmethod
    def default(cls) -> Self:
        """Return the default algorithm."""
        return cls(cls.MANDELBROT)

    @classmethod
    def list_algorithms(cls) -> list[str]:
        """List all known algorithms' names."""
        return [algo.value for algo in cls]

    @classmethod
    def get_algo_params(cls, value: str) -> ReactiveParams:
        """Return the parameters for the chosen algorithm."""
        match cls(value):
            case cls.MANDELBROT:
                return MandelbrotParams()
            case cls.JULIA:
                return JuliaParams()
            case cls.FERN:
                return FernParams()
            case cls.SIERPINSKI:
                return SierpinskiParams()
            case cls.BURNING_SHIP:
                return BurningShipParams()
            case _:
                msg = f"unknown algorithm '{value}'"
                raise ValueError(msg)

    @classmethod
    def get_algo_impl(cls, value: str) -> type[FractalAlgorithm]:
        """Return the implementation of the chosen algorithm."""
        match cls(value):
            case cls.MANDELBROT:
                return MandelbrotAlgo
            case cls.JULIA:
                return JuliaAlgo
            case cls.FERN:
                return FernAlgo
            case cls.SIERPINSKI:
                return SierpinskiAlgo
            case cls.BURNING_SHIP:
                return BurningShipAlgo
            case _:
                msg = f"unknown algorithm '{value}'"
                raise ValueError(msg)
