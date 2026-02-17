"""
Base scanner interface.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Set


@dataclass(frozen=True)
class Artifact:
    """Represents a build artifact."""

    path: Path
    type: str
    size_bytes: int = 0


def get_dir_size(path: Path) -> int:
    """Calculate the total size of a directory in bytes."""
    total_size = 0
    try:
        for p in path.rglob("*"):
            if p.is_file():
                total_size += p.stat().st_size
    except (OSError, PermissionError):
        # If we can't access some files, we'll return what we could find
        pass
    return total_size


class BaseScanner(ABC):
    """Base class for all build artifact scanners."""

    @abstractmethod
    def scan(self, root_path: Path, calculate_size: bool = True) -> Set[Artifact]:
        """
        Scan for build artifacts in the given root path.
        Returns a set of Artifacts to be removed.
        """
