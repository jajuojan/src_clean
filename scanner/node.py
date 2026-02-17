import os
from pathlib import Path
from typing import Set
from .base_scanner import BaseScanner


class NodeScanner(BaseScanner):
    def scan(self, root_path: Path) -> Set[Path]:
        artifacts: Set[Path] = set()
        for root, dirs, files in os.walk(root_path):
            current_path = Path(root)
            if "package.json" in files:
                node_modules = current_path / "node_modules"
                if node_modules.exists() and node_modules.is_dir():
                    artifacts.add(node_modules)
        return artifacts
