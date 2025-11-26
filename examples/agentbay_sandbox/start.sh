#!/bin/bash
# Start both backend and frontend servers

set -e  # Exit on error

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}Shutting down servers...${NC}"
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
        echo -e "${GREEN}Backend server stopped${NC}"
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
        echo -e "${GREEN}Frontend server stopped${NC}"
    fi
    exit 0
}

# Trap Ctrl+C and cleanup
trap cleanup SIGINT SIGTERM

# Check if .env file exists
if [ ! -f "$SCRIPT_DIR/.env" ]; then
    echo -e "${YELLOW}Warning: .env file not found. Creating from .env.example...${NC}"
    if [ -f "$SCRIPT_DIR/.env.example" ]; then
        cp "$SCRIPT_DIR/.env.example" "$SCRIPT_DIR/.env"
        echo -e "${YELLOW}Please edit .env file and add your API keys${NC}"
    else
        echo -e "${YELLOW}Please create .env file with DASHSCOPE_API_KEY and AGENTBAY_API_KEY${NC}"
    fi
fi

# Start backend server
echo -e "${BLUE}Starting backend server...${NC}"
cd "$SCRIPT_DIR"
uv run python -m backend.api_server &
BACKEND_PID=$!
echo -e "${GREEN}Backend server started (PID: $BACKEND_PID)${NC}"
echo -e "${BLUE}Backend API: http://localhost:8000${NC}"

# Wait a bit for backend to start
sleep 2

# Start frontend server
echo -e "${BLUE}Starting frontend server...${NC}"
cd "$FRONTEND_DIR"
npm run dev &
FRONTEND_PID=$!
echo -e "${GREEN}Frontend server started (PID: $FRONTEND_PID)${NC}"
echo -e "${BLUE}Frontend: http://localhost:5173${NC}"

echo -e "\n${GREEN}Both servers are running!${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop both servers${NC}\n"

# Wait for both processes
wait
