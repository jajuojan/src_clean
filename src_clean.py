"""
src-clean: A tool to detect and remove build artifacts.
"""

import argparse
import sys
from pathlib import Path
from typing import Set

from remover import DirectRemover, ScriptRemover
from scanner import Artifact, DotnetScanner, NodeScanner


def format_size(size_bytes: int) -> str:
    """Format bytes into a human-readable string."""
    size = float(size_bytes)
    for unit in ["B", "KiB", "MiB", "GiB", "TiB"]:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} PiB"


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
    parser.add_argument(
        "--no-size",
        action="store_true",
        help="Do not calculate or print artifact sizes",
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
        artifacts.update(scanner.scan(root_path, calculate_size=not args.no_size))

    if not artifacts:
        print("No artifacts found.")
        return

    sorted_artifacts = sorted(list(artifacts), key=lambda x: x.path)
    print(f"\nFound {len(sorted_artifacts)} artifact(s)...")

    if args.mode == "dry-run":
        total_size = 0
        for artifact in sorted_artifacts:
            path_str = f"  {artifact.path} [{artifact.type}]"
            if args.no_size:
                print(path_str)
            else:
                size_str = f"({format_size(artifact.size_bytes)})"
                print(f"{path_str} {size_str}")
                total_size += artifact.size_bytes

        if not args.no_size:
            print(f"\nTotal potential space savings: {format_size(total_size)}")

    elif args.mode == "script":
        script_remover = ScriptRemover()
        script_remover.remove([a.path for a in sorted_artifacts])

    elif args.mode == "delete":
        direct_remover = DirectRemover()
        result = direct_remover.remove([a.path for a in sorted_artifacts])

        # Report space freed
        if result.removed and not args.no_size:
            freed_bytes = 0
            # Map Path to size from our sorted_artifacts list
            path_to_size = {a.path: a.size_bytes for a in sorted_artifacts}
            for removed_path in result.removed:
                freed_bytes += path_to_size.get(removed_path, 0)
            print(f"\nTotal space freed: {format_size(freed_bytes)}")

        if not result.success:
            sys.exit(1)


if __name__ == "__main__":
    main()
