"""
Base remover interface.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List


@dataclass
class RemovalResult:
    """Represents the result of a removal operation."""

    success: bool
    removed: List[Path] = field(default_factory=list)
    failed: List[Path] = field(default_factory=list)
    skipped: List[Path] = field(default_factory=list)


class BaseRemover(ABC):
    """Base class for all removers."""

    @abstractmethod
    def remove(self, artifacts: Iterable[Path]) -> RemovalResult:
        """Remove the given artifacts.

        Returns:
            A RemovalResult object containing the results of the operation.
        """
