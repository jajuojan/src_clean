"""
Artifact Cleaner: A tool to detect and remove build artifacts.
"""

import argparse
from pathlib import Path
from typing import Set
from scanner import NodeScanner, DotnetScanner
from remover import DirectRemover, ScriptRemover


def main() -> None:
    """Main entry point for the tool."""
    parser = argparse.ArgumentParser(description="Detect and remove build artifacts.")
    parser.add_argument("path", nargs="?", default=".", help="Directory to scan")
    parser.add_argument(
        "--mode",
        choices=["dry-run", "script", "delete"],
        default="dry-run",
        help=(
            "Action to take: dry-run (list), "
            "script (print rm commands to stdout), delete (remove files)"
        ),
    )

    args = parser.parse_args()
    root_path = Path(args.path).resolve()

    if not root_path.exists():
        print(f"Path does not exist: {root_path}")
        return

    print(f"Scanning {root_path}...")

    scanners = [NodeScanner(), DotnetScanner()]
    artifacts: Set[Path] = set()
    for scanner in scanners:
        artifacts.update(scanner.scan(root_path))

    if not artifacts:
        print("No artifacts found.")
        return

    sorted_artifacts = sorted(list(artifacts))

    if args.mode == "dry-run":
        print("\nFound artifacts:")
        for artifact in sorted_artifacts:
            print(f"  {artifact}")

    elif args.mode == "script":
        script_remover = ScriptRemover()
        script_remover.remove(sorted_artifacts)

    elif args.mode == "delete":
        direct_remover = DirectRemover()
        direct_remover.remove(sorted_artifacts)


if __name__ == "__main__":
    main()
