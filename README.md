# Artifact Cleaner

A Python program that detects and helps in removing build artifacts for Node.js and .NET projects.

## Features

- **Multi-language Support**:
    - **Node.js**: Detects `node_modules` folders in directories containing `package.json`.
    - **.NET**: Detects `bin` and `obj` folders. It uses the `dotnet` SDK to identify exact output paths when available, falling back to standard names if necessary.
- **Multiple Deletion Modes**:
    - **Dry Run**: List all detected artifacts without deleting them.
    - **Script Generation**: Generate a shell script (`clean.sh`) containing `rm -rf` commands for manual execution.
    - **Direct Deletion**: Remove artifacts directly using Python.

## Usage

You can run the script using Python:

```bash
# List all detected artifacts (dry-run)
python main.py .

# Generate a cleanup script
python main.py . --mode script --output my_clean.sh

# Delete artifacts directly
python main.py . --mode delete
```

### Arguments

- `path`: (Optional) The directory to scan. Defaults to the current directory (`.`).
- `--mode`: The action to take. Options: `dry-run` (default), `script`, `delete`.
- `--output`: The name of the output file when using `script` mode. Defaults to `clean.sh`.

## Requirements

- Python 3.13 or higher
- (Optional) .NET SDK for more accurate .NET artifact detection
