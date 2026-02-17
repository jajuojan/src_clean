"""
Scanner for Node.js build artifacts.
"""

import os
from pathlib import Path
from typing import Set

from .base_scanner import BaseScanner


class NodeScanner(BaseScanner):
    """Scanner for node_modules folders."""

    def scan(self, root_path: Path) -> Set[Path]:
        artifacts: Set[Path] = set()
        for root, _, files in os.walk(root_path):
            if "package.json" in files:
                node_modules = Path(os.path.join(root, "node_modules"))
                if node_modules.exists() and node_modules.is_dir():
                    artifacts.add(node_modules)
        return artifacts
