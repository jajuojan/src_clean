import os
import subprocess
from pathlib import Path
from typing import Set
from .base_scanner import BaseScanner


class DotnetScanner(BaseScanner):
    def scan(self, root_path: Path) -> Set[Path]:
        artifacts: Set[Path] = set()
        for root, dirs, files in os.walk(root_path):
            current_path = Path(root)
            for file in files:
                if file.endswith((".csproj", ".fsproj", ".vbproj")):
                    artifacts.update(self._scan_dotnet(current_path / file))
        return artifacts

    def _scan_dotnet(self, project_file: Path) -> Set[Path]:
        artifacts: Set[Path] = set()
        try:
            # Get BaseOutputPath
            result = subprocess.run(
                ["dotnet", "msbuild", str(project_file), "-getProperty:BaseOutputPath"],
                capture_output=True,
                text=True,
                check=True
            )
            base_output = result.stdout.strip()
            if base_output:
                path = (project_file.parent / base_output).resolve()
                if path.exists() and path.is_dir():
                    artifacts.add(path)

            # Get BaseIntermediateOutputPath
            result = subprocess.run(
                ["dotnet", "msbuild", str(project_file), "-getProperty:BaseIntermediateOutputPath"],
                capture_output=True,
                text=True,
                check=True
            )
            base_intermediate = result.stdout.strip()
            if base_intermediate:
                path = (project_file.parent / base_intermediate).resolve()
                if path.exists() and path.is_dir():
                    artifacts.add(path)
        except subprocess.CalledProcessError:
            # Fallback to common names if dotnet fails
            for name in ["bin", "obj"]:
                path = project_file.parent / name
                if path.exists() and path.is_dir():
                    artifacts.add(path)
        return artifacts
