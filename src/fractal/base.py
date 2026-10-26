"""Common base utils for fractal algorithms."""

from abc import ABC, abstractmethod

from common.camera import Camera
from common.reactive_params import ReactiveParams
from common.types import Lattice


class FractalAlgorithm[T: ReactiveParams](ABC):
    """Abstract base class for fractal algorithms."""

    @staticmethod
    @abstractmethod
    def default_camera(width: int, height: int) -> Camera:
        """Return the default `Camera` object for the fractal."""
        ...

    @staticmethod
    @abstractmethod
    def generate_frame(camera: Camera, params: T) -> Lattice:
        """Generate a frame of the fractal."""
        ...
