"""
Tests for the CLI arguments.
"""

import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
from src_clean import main


class TestCLI(unittest.TestCase):
    """Tests for the command-line interface."""

    @patch("src_clean.NodeScanner")
    @patch("src_clean.DotnetScanner")
    @patch("src_clean.argparse.ArgumentParser.parse_args")
    @patch("sys.argv", ["src_clean.py", "."])
    @patch("pathlib.Path.exists", return_value=True)
    @patch("pathlib.Path.resolve", return_value=Path("."))
    def test_default_scanners(
        self,
        _mock_resolve: MagicMock,
        _mock_exists: MagicMock,
        mock_args: MagicMock,
        mock_dotnet: MagicMock,
        mock_node: MagicMock,
    ) -> None:
        """Test that all scanners are used by default."""
        mock_args.return_value = MagicMock(
            path=".", mode="dry-run", scanners=["node", "dotnet"]
        )

        # We need to mock the scan method to return an empty set to avoid further logic
        mock_node.return_value.scan.return_value = set()
        mock_dotnet.return_value.scan.return_value = set()

        with patch("builtins.print"):
            main()

        mock_node.assert_called_once()
        mock_dotnet.assert_called_once()

    @patch("src_clean.NodeScanner")
    @patch("src_clean.DotnetScanner")
    @patch("src_clean.argparse.ArgumentParser.parse_args")
    @patch("sys.argv", ["src_clean.py", ".", "--scanners", "node"])
    @patch("pathlib.Path.exists", return_value=True)
    @patch("pathlib.Path.resolve", return_value=Path("."))
    def test_single_scanner(
        self,
        _mock_resolve: MagicMock,
        _mock_exists: MagicMock,
        mock_args: MagicMock,
        mock_dotnet: MagicMock,
        mock_node: MagicMock,
    ) -> None:
        """Test that only the specified scanner is used."""
        mock_args.return_value = MagicMock(path=".", mode="dry-run", scanners=["node"])

        mock_node.return_value.scan.return_value = set()

        with patch("builtins.print"):
            main()

        mock_node.assert_called_once()
        mock_dotnet.assert_not_called()

    @patch("src_clean.NodeScanner")
    @patch("src_clean.DotnetScanner")
    @patch("src_clean.argparse.ArgumentParser.parse_args")
    @patch("sys.argv", ["src_clean.py", ".", "--scanners", "all"])
    @patch("pathlib.Path.exists", return_value=True)
    @patch("pathlib.Path.resolve", return_value=Path("."))
    def test_all_scanner_option(
        self,
        _mock_resolve: MagicMock,
        _mock_exists: MagicMock,
        mock_args: MagicMock,
        mock_dotnet: MagicMock,
        mock_node: MagicMock,
    ) -> None:
        """Test that 'all' option uses all scanners."""
        mock_args.return_value = MagicMock(path=".", mode="dry-run", scanners=["all"])

        mock_node.return_value.scan.return_value = set()
        mock_dotnet.return_value.scan.return_value = set()

        with patch("builtins.print"):
            main()

        mock_node.assert_called_once()
        mock_dotnet.assert_called_once()


if __name__ == "__main__":
    unittest.main()
