# src_clean

A Python tool to detect and remove build artifacts for Node.js and .NET projects. It helps you reclaim disk space by identifying and cleaning up temporary build files.

## Features

- **Multi-language Support**:
  - **Node.js**: Detects `node_modules` folders in directories containing `package.json`.
  - **.NET**: Detects `bin` and `obj` folders using the `dotnet` SDK for high accuracy.
- **Disk Space Analysis**: Calculates and displays the size of each artifact and total potential savings.
- **Multiple Deletion Modes**:
  - **Dry Run** (default): Safely list all detected artifacts and their sizes.
  - **Script Generation**: Generate a POSIX-compliant shell script to stdout for manual execution.
  - **Direct Deletion**: Interactive removal with confirmation prompts and a final report of space freed.
- **Selective Scanning**: Choose specific scanners or run all of them at once.

## Usage

You can run the script using Python:

```bash
# List all detected artifacts (dry-run)
python src_clean.py .

# Generate a cleanup script to a file
python src_clean.py . --mode script > clean.sh

# Or pipe directly to a shell (use with caution)
python src_clean.py . --mode script | sh

# Delete artifacts directly
python src_clean.py . --mode delete
```

### Arguments

- `path`: **(Required)** The directory to scan.
- `--mode`: The action to take.
  - `dry-run` (default): List artifacts and sizes.
  - `script`: Print `rm` commands.
  - `delete`: Interactively delete artifacts.
- `--no-size`: Do not calculate or print artifact sizes (improves performance on large directories).

## Installation & Requirements

- Python 3.13 or higher.
- (Recommended) `.NET SDK` installed for `.NET` scanning.

No external Python dependencies are required for the core functionality.
