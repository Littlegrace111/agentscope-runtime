#!/bin/bash
# Simple version using jq (recommended)

set -e

API_BASE_URL="${API_BASE_URL:-http://localhost:8000}"
SANDBOX_TYPE="${1:-linux}"

echo "Creating ${SANDBOX_TYPE} sandbox..."

# Create sandbox
CREATE_RESPONSE=$(curl -s -X POST "${API_BASE_URL}/api/sandboxes?sandbox_type=${SANDBOX_TYPE}")

# Extract sandbox_id
SANDBOX_ID=$(echo "$CREATE_RESPONSE" | jq -r '.sandbox_id')

if [ "$SANDBOX_ID" = "null" ] || [ -z "$SANDBOX_ID" ]; then
    echo "Error: Failed to create sandbox"
    echo "$CREATE_RESPONSE" | jq '.'
    exit 1
fi

echo "Sandbox created: $SANDBOX_ID"
echo "Getting resource_url..."

# Get resource_url
RESOURCE_URL_RESPONSE=$(curl -s "${API_BASE_URL}/api/sandboxes/${SANDBOX_ID}/resource_url")

# Extract resource_url
RESOURCE_URL=$(echo "$RESOURCE_URL_RESPONSE" | jq -r '.resource_url')

if [ "$RESOURCE_URL" = "null" ] || [ -z "$RESOURCE_URL" ]; then
    echo "Error: Failed to get resource_url"
    echo "$RESOURCE_URL_RESPONSE" | jq '.'
    exit 1
fi

echo ""
echo "Resource URL:"
echo "$RESOURCE_URL"
