"""
src-clean: A tool to detect and remove build artifacts.
"""

import argparse
import sys
from pathlib import Path
from typing import Set

from remover import DirectRemover, ScriptRemover
from scanner import Artifact, DotnetScanner, NodeScanner


def main() -> None:
    """Main entry point for the tool."""
    parser = argparse.ArgumentParser(description="Detect and remove build artifacts.")
    parser.add_argument("path", help="Directory to scan")
    parser.add_argument(
        "--mode",
        choices=["dry-run", "script", "delete"],
        default="dry-run",
        help=(
            "Action to take: dry-run (list), "
            "script (print rm commands to stdout), delete (remove files)"
        ),
    )
    parser.add_argument(
        "--scanners",
        nargs="+",
        choices=["node", "dotnet", "all"],
        default=["all"],
        help="Scanners to use (default: all)",
    )

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()
    root_path = Path(args.path).resolve()

    if not root_path.exists():
        print(f"Path does not exist: {root_path}")
        return

    scanner_map = {
        "node": NodeScanner,
        "dotnet": DotnetScanner,
    }

    selected_scanners = args.scanners
    if "all" in selected_scanners:
        selected_scanners = list(scanner_map.keys())

    scanners = [scanner_map[s]() for s in selected_scanners]
    artifacts: Set[Artifact] = set()

    print(f"Scanning {root_path}...")
    for scanner in scanners:
        artifacts.update(scanner.scan(root_path))

    if not artifacts:
        print("No artifacts found.")
        return

    sorted_artifacts = sorted(list(artifacts), key=lambda x: x.path)
    print(f"\nFound {len(sorted_artifacts)} artifact(s)...")

    if args.mode == "dry-run":
        for artifact in sorted_artifacts:
            print(f"  {artifact.path} [{artifact.type}]")

    elif args.mode == "script":
        script_remover = ScriptRemover()
        script_remover.remove([a.path for a in sorted_artifacts])

    elif args.mode == "delete":
        direct_remover = DirectRemover()
        result = direct_remover.remove([a.path for a in sorted_artifacts])
        if not result.success:
            sys.exit(1)


if __name__ == "__main__":
    main()
