"""
Tests for the NodeScanner class.
"""

import shutil
import tempfile
import unittest
from pathlib import Path

from scanner.node import NodeScanner


class TestNodeScanner(unittest.TestCase):
    """Unit tests for NodeScanner."""

    def setUp(self) -> None:
        self.test_dir = Path(tempfile.mkdtemp())
        self.scanner = NodeScanner()

    def tearDown(self) -> None:
        shutil.rmtree(self.test_dir)

    def test_scan_finds_node_modules(self) -> None:
        """Test that scan finds node_modules when package.json exists."""
        # Create a project with package.json and node_modules
        project_dir = self.test_dir / "project"
        project_dir.mkdir()
        (project_dir / "package.json").touch()
        node_modules = project_dir / "node_modules"
        node_modules.mkdir()

        artifacts = self.scanner.scan(self.test_dir)

        self.assertEqual(len(artifacts), 1)
        artifact = list(artifacts)[0]
        self.assertEqual(artifact.path, node_modules)
        self.assertEqual(artifact.type, "Node.js")
        self.assertEqual(artifact.size_bytes, 0)

    def test_scan_ignores_node_modules_without_package_json(self) -> None:
        """Test that scan ignores node_modules if no package.json is present."""
        # Create a directory with node_modules but NO package.json
        other_dir = self.test_dir / "other"
        other_dir.mkdir()
        node_modules = other_dir / "node_modules"
        node_modules.mkdir()

        artifacts = self.scanner.scan(self.test_dir)

        self.assertEqual(len(artifacts), 0)

    def test_scan_recursive(self) -> None:
        """Test that scan finds nested projects with node_modules."""
        # Create nested projects
        p1 = self.test_dir / "p1"
        p1.mkdir()
        (p1 / "package.json").touch()
        n1 = p1 / "node_modules"
        n1.mkdir()

        p2 = p1 / "nested" / "p2"
        p2.mkdir(parents=True)
        (p2 / "package.json").touch()
        n2 = p2 / "node_modules"
        n2.mkdir()

        artifacts = self.scanner.scan(self.test_dir)

        self.assertEqual(len(artifacts), 2)
        paths = {a.path for a in artifacts}
        self.assertIn(n1, paths)
        self.assertIn(n2, paths)
        for a in artifacts:
            self.assertEqual(a.type, "Node.js")
            self.assertEqual(a.size_bytes, 0)


if __name__ == "__main__":
    unittest.main()
