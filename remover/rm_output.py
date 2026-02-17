"""
Generate a shell script to remove build artifacts.
"""

import os
from pathlib import Path
from typing import Iterable

from .base_delete import BaseRemover


class ScriptRemover(BaseRemover):
    """Prints shell commands to remove artifacts to stdout."""

    def remove(self, artifacts: Iterable[Path]) -> None:
        sorted_artifacts = sorted(list(artifacts))
        if os.name != "nt":
            print("#!/bin/sh")
        for artifact in sorted_artifacts:
            print(f'rm -rf "{artifact}"')
