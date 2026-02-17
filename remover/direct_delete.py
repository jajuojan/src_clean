"""
Directly remove build artifacts from the filesystem.
"""

import shutil
from pathlib import Path
from typing import Iterable

from .base_delete import BaseRemover


class DirectRemover(BaseRemover):
    """Removes artifacts directly from the filesystem."""

    def remove(self, artifacts: Iterable[Path]) -> None:
        print("\nDeleting artifacts...")
        for artifact in artifacts:
            try:
                print(f"  Removing {artifact}...")
                if artifact.is_dir():
                    shutil.rmtree(artifact)
                else:
                    artifact.unlink()
            except (OSError, PermissionError) as e:
                print(f"  Error removing {artifact}: {e}")
        print("Done.")
