"""
Directly remove build artifacts from the filesystem.
"""

import shutil
from pathlib import Path
from typing import Iterable

from .base_delete import BaseRemover, RemovalResult


class DirectRemover(BaseRemover):
    """Removes artifacts directly from the filesystem."""

    def remove(self, artifacts: Iterable[Path]) -> RemovalResult:
        print("\nDeleting artifacts...")
        result = RemovalResult(success=True)
        for artifact in artifacts:
            try:
                response = input(f"  Remove {artifact}? [y/N] ").lower().strip()
                if response != "y":
                    print(f"  Skipping {artifact}...")
                    result.skipped.append(artifact)
                    continue

                print(f"  Removing {artifact}...")
                if artifact.is_dir():
                    shutil.rmtree(artifact)
                else:
                    artifact.unlink()
                result.removed.append(artifact)
            except (OSError, PermissionError) as e:
                print(f"  Error removing {artifact}: {e}")
                result.failed.append(artifact)
                result.success = False
            except EOFError:
                print("\nInterrupted.")
                result.success = False
                break
        return result
