"""
Scanner for Node.js build artifacts.
"""

import os
from pathlib import Path
from typing import Set

from .base_scanner import Artifact, BaseScanner, get_dir_size


class NodeScanner(BaseScanner):
    """Scanner for node_modules folders."""

    def scan(self, root_path: Path, calculate_size: bool = True) -> Set[Artifact]:
        artifacts: Set[Artifact] = set()
        for root, _, files in os.walk(root_path):
            if "package.json" in files:
                node_modules = Path(os.path.join(root, "node_modules"))
                if node_modules.exists() and node_modules.is_dir():
                    size = get_dir_size(node_modules) if calculate_size else 0
                    artifacts.add(
                        Artifact(
                            path=node_modules,
                            type="Node.js",
                            size_bytes=size,
                        )
                    )
        return artifacts
