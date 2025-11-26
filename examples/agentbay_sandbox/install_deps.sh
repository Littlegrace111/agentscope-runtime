#!/bin/bash
# Install dependencies from pyproject.toml using uv

set -e

# Get the script directory and project root
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "Installing dependencies from pyproject.toml..."

# Ensure virtual environment exists in agentbay_sandbox directory
if [ ! -d "$SCRIPT_DIR/.venv" ]; then
    echo "Creating virtual environment..."
    cd "$SCRIPT_DIR"
    uv venv
fi

# Activate the virtual environment for subsequent commands
# Note: uv pip install will automatically use the .venv in current directory
cd "$SCRIPT_DIR"

# First, install agentscope-runtime from source (editable mode)
# Use the virtual environment from agentbay_sandbox directory
echo "Installing agentscope-runtime from source..."
cd "$PROJECT_ROOT"
uv pip install -e . --python "$SCRIPT_DIR/.venv/bin/python"

# Return to agentbay_sandbox directory
cd "$SCRIPT_DIR"

# Install main dependencies
echo "Installing main dependencies..."
uv pip install \
    "fastapi>=0.104.0" \
    "uvicorn[standard]>=0.24.0" \
    "websockets>=12.0" \
    "pydantic>=2.0.0" \
    "python-dotenv>=1.0.0" \
    "agentscope>=0.1.0" \
    "aiofiles>=23.0.0"

# Install dev dependencies if requested
if [ "$1" == "--dev" ]; then
    echo "Installing dev dependencies..."
    uv pip install \
        "pytest>=7.0.0" \
        "pytest-asyncio>=0.21.0" \
        "black>=23.0.0" \
        "ruff>=0.1.0"
fi

echo "Dependencies installed successfully!"
