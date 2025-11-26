#!/bin/bash
# Script to create a sandbox and get its resource_url

set -e

# Configuration
API_BASE_URL="${API_BASE_URL:-http://localhost:8000}"
SANDBOX_TYPE="${1:-linux}"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Creating ${SANDBOX_TYPE} sandbox ===${NC}"

# Step 1: Create sandbox
echo -e "${YELLOW}Step 1: Creating sandbox...${NC}"
CREATE_RESPONSE=$(curl -s -X POST "${API_BASE_URL}/api/sandboxes?sandbox_type=${SANDBOX_TYPE}")

# Check if curl was successful
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to connect to API server${NC}"
    exit 1
fi

# Extract sandbox_id using jq (if available) or grep/sed
if command -v jq &> /dev/null; then
    SUCCESS=$(echo "$CREATE_RESPONSE" | jq -r '.success // false')
    SANDBOX_ID=$(echo "$CREATE_RESPONSE" | jq -r '.sandbox_id // empty')
    ERROR=$(echo "$CREATE_RESPONSE" | jq -r '.error // empty')
else
    # Fallback: use grep and sed if jq is not available
    SUCCESS=$(echo "$CREATE_RESPONSE" | grep -o '"success"[[:space:]]*:[[:space:]]*true' > /dev/null && echo "true" || echo "false")
    SANDBOX_ID=$(echo "$CREATE_RESPONSE" | grep -o '"sandbox_id"[[:space:]]*:[[:space:]]*"[^"]*"' | sed 's/.*"sandbox_id"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/')
    ERROR=$(echo "$CREATE_RESPONSE" | grep -o '"error"[[:space:]]*:[[:space:]]*"[^"]*"' | sed 's/.*"error"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/')
fi

# Check if creation was successful
if [ "$SUCCESS" != "true" ] || [ -z "$SANDBOX_ID" ]; then
    echo -e "${RED}Error: Failed to create sandbox${NC}"
    echo "Response: $CREATE_RESPONSE"
    if [ -n "$ERROR" ]; then
        echo -e "${RED}Error message: $ERROR${NC}"
    fi
    exit 1
fi

echo -e "${GREEN}✓ Sandbox created successfully${NC}"
echo -e "${GREEN}  Sandbox ID: ${SANDBOX_ID}${NC}"
echo ""

# Step 2: Get resource_url
echo -e "${BLUE}=== Getting resource_url for sandbox ${SANDBOX_ID} ===${NC}"
echo -e "${YELLOW}Step 2: Fetching resource_url...${NC}"

RESOURCE_URL_RESPONSE=$(curl -s "${API_BASE_URL}/api/sandboxes/${SANDBOX_ID}/resource_url")

# Check if curl was successful
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to connect to API server${NC}"
    exit 1
fi

# Extract resource_url
if command -v jq &> /dev/null; then
    RESOURCE_SUCCESS=$(echo "$RESOURCE_URL_RESPONSE" | jq -r '.success // false')
    RESOURCE_URL=$(echo "$RESOURCE_URL_RESPONSE" | jq -r '.resource_url // empty')
    RESOURCE_ERROR=$(echo "$RESOURCE_URL_RESPONSE" | jq -r '.error // empty')
else
    # Fallback: use grep and sed if jq is not available
    RESOURCE_SUCCESS=$(echo "$RESOURCE_URL_RESPONSE" | grep -o '"success"[[:space:]]*:[[:space:]]*true' > /dev/null && echo "true" || echo "false")
    RESOURCE_URL=$(echo "$RESOURCE_URL_RESPONSE" | grep -o '"resource_url"[[:space:]]*:[[:space:]]*"[^"]*"' | sed 's/.*"resource_url"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/')
    RESOURCE_ERROR=$(echo "$RESOURCE_URL_RESPONSE" | grep -o '"error"[[:space:]]*:[[:space:]]*"[^"]*"' | sed 's/.*"error"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/')
fi

# Check if getting resource_url was successful
if [ "$RESOURCE_SUCCESS" != "true" ] || [ -z "$RESOURCE_URL" ]; then
    echo -e "${RED}Error: Failed to get resource_url${NC}"
    echo "Response: $RESOURCE_URL_RESPONSE"
    if [ -n "$RESOURCE_ERROR" ]; then
        echo -e "${RED}Error message: $RESOURCE_ERROR${NC}"
    fi
    exit 1
fi

echo -e "${GREEN}✓ Resource URL retrieved successfully${NC}"
echo ""
echo -e "${BLUE}=== Result ===${NC}"
echo -e "${GREEN}Sandbox ID: ${SANDBOX_ID}${NC}"
echo -e "${GREEN}Sandbox Type: ${SANDBOX_TYPE}${NC}"
echo -e "${GREEN}Resource URL:${NC}"
echo "$RESOURCE_URL"
echo ""
echo -e "${YELLOW}You can open this URL in your browser to access the sandbox GUI${NC}"
