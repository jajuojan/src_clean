"""
Scanner for .NET build artifacts.
"""

import json
import os
import subprocess
from pathlib import Path
from typing import Set

from .base_scanner import BaseScanner


class DotnetScanner(BaseScanner):
    """Scanner for .NET bin and obj folders."""

    def __init__(self) -> None:
        self._is_available = self._check_dotnet_tool()

    def _check_dotnet_tool(self) -> bool:
        """Check if the dotnet tool is available."""
        try:
            subprocess.run(
                ["dotnet", "--version"],
                capture_output=True,
                check=True,
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def scan(self, root_path: Path) -> Set[Path]:
        """Scan for build artifacts in the given root path."""
        if not self._is_available:
            return set()

        artifacts: Set[Path] = set()
        for root, _, files in os.walk(root_path):
            current_path = Path(root)
            for file in files:
                if file.endswith((".csproj", ".fsproj", ".vbproj")):
                    artifacts.update(self._scan_dotnet(current_path / file))
        return artifacts

    def _scan_dotnet(self, project_file: Path) -> Set[Path]:
        artifacts: Set[Path] = set()

        # Get both BaseOutputPath and BaseIntermediateOutputPath in a single call
        result = subprocess.run(
            [
                "dotnet",
                "msbuild",
                str(project_file),
                "-getProperty:BaseOutputPath,BaseIntermediateOutputPath",
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        # When multiple properties are requested, msbuild returns a JSON object
        data = json.loads(result.stdout)
        props = data.get("Properties", {})

        for key in ["BaseOutputPath", "BaseIntermediateOutputPath"]:
            val = props.get(key)
            if val:
                path = (project_file.parent / val).resolve()
                if path.exists() and path.is_dir():
                    artifacts.add(path)

        return artifacts
