# src_clean

A Python program that detects and helps in removing build artifacts for Node.js and .NET projects.

## Features

- **Multi-language Support**:
  - **Node.js**: Detects `node_modules` folders in directories containing `package.json`.
  - **.NET**: Detects `bin` and `obj` folders. It uses the `dotnet` SDK to identify exact output paths when available.
- **Multiple Deletion Modes**:
  - **Dry Run**: List all detected artifacts without deleting them.
  - **Script Generation**: Print a portable shell script to stdout containing `rm -rf` commands for manual execution (redirect to a file if desired).
  - **Direct Deletion**: Remove artifacts directly using Python.

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

- `path`: (Optional) The directory to scan. Defaults to the current directory (`.`).
- `--mode`: The action to take. Options: `dry-run` (default), `script`, `delete`.

## Requirements

- Python 3.13 or higher
- (Optional) .NET SDK for more accurate .NET artifact detection
