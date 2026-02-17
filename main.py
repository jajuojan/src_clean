import argparse
import os
import shutil
from pathlib import Path
from typing import Set
from scanner import NodeScanner, DotnetScanner


def main():
    parser = argparse.ArgumentParser(description="Detect and remove build artifacts.")
    parser.add_argument("path", nargs="?", default=".", help="Directory to scan")
    parser.add_argument("--mode", choices=["dry-run", "script", "delete"], default="dry-run",
                        help="Action to take: dry-run (list), script (output rm commands), delete (remove files)")
    parser.add_argument("--output", default="clean.sh", help="Output file for script mode")

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
        with open(args.output, "w") as f:
            if os.name == 'nt':
                 # For Windows, provide standard rm which works in git bash / wsl / etc.
                 f.write("#!/bin/sh\n")
            else:
                 f.write("#!/bin/sh\n")
            for artifact in sorted_artifacts:
                f.write(f"rm -rf \"{artifact}\"\n")
        print(f"\nCreated {args.output} with {len(sorted_artifacts)} commands.")

    elif args.mode == "delete":
        print("\nDeleting artifacts...")
        for artifact in sorted_artifacts:
            try:
                print(f"  Removing {artifact}...")
                if artifact.is_dir():
                    shutil.rmtree(artifact)
                else:
                    artifact.unlink()
            except Exception as e:
                print(f"  Error removing {artifact}: {e}")
        print("Done.")


if __name__ == "__main__":
    main()
