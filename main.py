import argparse
import os
import shutil
import subprocess
from pathlib import Path
from typing import List, Set


class ArtifactScanner:
    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.artifacts: Set[Path] = set()

    def scan(self):
        for root, dirs, files in os.walk(self.root_path):
            root_path = Path(root)
            
            # Node.js
            if "package.json" in files:
                node_modules = root_path / "node_modules"
                if node_modules.exists() and node_modules.is_dir():
                    self.artifacts.add(node_modules)
            
            # .NET
            for file in files:
                if file.endswith((".csproj", ".fsproj", ".vbproj")):
                    self._scan_dotnet(root_path / file)

    def _scan_dotnet(self, project_file: Path):
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
                    self.artifacts.add(path)

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
                    self.artifacts.add(path)
        except subprocess.CalledProcessError:
            # Fallback to common names if dotnet fails
            for name in ["bin", "obj"]:
                path = project_file.parent / name
                if path.exists() and path.is_dir():
                    self.artifacts.add(path)


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
    scanner = ArtifactScanner(root_path)
    scanner.scan()

    if not scanner.artifacts:
        print("No artifacts found.")
        return

    sorted_artifacts = sorted(list(scanner.artifacts))

    if args.mode == "dry-run":
        print("\nFound artifacts:")
        for artifact in sorted_artifacts:
            print(f"  {artifact}")
    
    elif args.mode == "script":
        with open(args.output, "w") as f:
            if os.name == 'nt':
                 # For Windows, maybe both? The prompt said 'rm' command.
                 # I'll provide standard rm which works in git bash / wsl / etc.
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
