#!/bin/bash
# Start backend server only

cd "$(dirname "$0")"
uv run python -m backend.api_server
