#!/bin/bash

set -eo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
rm -f requirements.txt
rm -f requirements_linux_arm64.txt
uv pip compile pyproject.toml --all-extras -o requirements.txt --generate-hashes
echo "--platform=manylinux_2_17_aarch64" >> requirements_linux_arm64.txt
cat requirements.txt >> requirements_linux_arm64.txt

# Update BUILD.bazel with the extracted dependencies
uv run python update_deps.py