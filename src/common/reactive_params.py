"""Abstract base class for reactive parameters."""

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any

WrappedSetattr = Callable[[Any, str, Any], None]


class ReactiveParams(ABC):
    """Abstract base class for parameters that redraw on change."""

    @abstractmethod
    def build_dpg_params(self, parent: str, setattr_: WrappedSetattr) -> None:
        """Build a tab of `dpg` parameters."""
        ...
