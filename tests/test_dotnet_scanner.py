"""
Tests for the DotnetScanner class.
"""

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from typing import Any, Tuple
from unittest.mock import patch

from scanner.dotnet import DotnetScanner


class TestDotnetScanner(unittest.TestCase):
    """Unit tests for DotnetScanner."""

    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp())

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir)

    def _make_project(self, name: str = "app") -> Tuple[Path, Path]:
        proj_dir = self.temp_dir / name
        proj_dir.mkdir(parents=True, exist_ok=True)
        csproj = proj_dir / f"{name}.csproj"
        csproj.write_text(
            '<Project Sdk="Microsoft.NET.Sdk"></Project>', encoding="utf-8"
        )
        return proj_dir, csproj

    def test_returns_empty_when_dotnet_not_available(self) -> None:
        """Test that scan returns empty set if dotnet tool is not found."""
        with patch("subprocess.run", side_effect=FileNotFoundError):
            scanner = DotnetScanner()
            artifacts = scanner.scan(self.temp_dir)
            self.assertEqual(artifacts, set())

    def test_finds_paths_from_msbuild_properties(self) -> None:
        """Test that scan finds bin and obj paths reported by msbuild."""
        proj_dir, csproj = self._make_project("lib1")

        def fake_run(args: Any, **_kwargs: Any) -> subprocess.CompletedProcess:
            if args[:2] == ["dotnet", "--version"]:
                return subprocess.CompletedProcess(
                    args=args, returncode=0, stdout="8.0.1"
                )
            if args[:3] == ["dotnet", "msbuild", str(csproj)]:
                props = {
                    "Properties": {
                        "BaseOutputPath": "bin/",
                        "BaseIntermediateOutputPath": "obj/",
                    }
                }
                return subprocess.CompletedProcess(
                    args=args, returncode=0, stdout=json.dumps(props)
                )
            raise AssertionError(f"Unexpected subprocess.run call: {args}")

        with patch("subprocess.run", side_effect=fake_run):
            # Create directories that msbuild reports
            bin_dir = (proj_dir / "bin").resolve()
            obj_dir = (proj_dir / "obj").resolve()
            bin_dir.mkdir(parents=True, exist_ok=True)
            obj_dir.mkdir(parents=True, exist_ok=True)

            scanner = DotnetScanner()
            artifacts = scanner.scan(self.temp_dir)
            paths = {a.path for a in artifacts}
            self.assertIn(bin_dir, paths)
            self.assertIn(obj_dir, paths)
            self.assertEqual(len(artifacts), 2)
            for a in artifacts:
                self.assertEqual(a.type, ".NET")
                self.assertEqual(a.size_bytes, 0)

    def test_ignores_nonexistent_paths_from_msbuild(self) -> None:
        """Test that scan ignores paths that do not exist on disk."""
        _, csproj = self._make_project("lib2")

        def fake_run(args: Any, **_kwargs: Any) -> subprocess.CompletedProcess:
            if args[:2] == ["dotnet", "--version"]:
                return subprocess.CompletedProcess(
                    args=args, returncode=0, stdout="8.0.1"
                )
            if args[:3] == ["dotnet", "msbuild", str(csproj)]:
                props = {
                    "Properties": {
                        "BaseOutputPath": "bin/",
                        "BaseIntermediateOutputPath": "obj/",
                    }
                }
                return subprocess.CompletedProcess(
                    args=args, returncode=0, stdout=json.dumps(props)
                )
            raise AssertionError(f"Unexpected subprocess.run call: {args}")

        with patch("subprocess.run", side_effect=fake_run):
            # Do NOT create bin/ or obj/ directories
            scanner = DotnetScanner()
            artifacts = scanner.scan(self.temp_dir)
            self.assertEqual(artifacts, set())


if __name__ == "__main__":
    unittest.main()
