#!/bin/bash
#
# Setup script for Lemlist Official Skill
#
# Usage: ./setup.sh

set -e

echo "========================================"
echo "Lemlist Official Skill Setup"
echo "========================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Python 3 found: $(python3 --version)"

# Check pip
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}Error: pip3 is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} pip3 found"

# Check API key
if [ -z "$LEMLIST_API_KEY" ]; then
    echo -e "${YELLOW}⚠ Warning: LEMLIST_API_KEY not set${NC}"
    echo ""
    echo "Please set your API key:"
    echo "  export LEMLIST_API_KEY='your_api_key_here'"
    echo ""
    echo "Get your API key from: https://app.lemlist.com/settings/integrations"
    echo ""
else
    echo -e "${GREEN}✓${NC} LEMLIST_API_KEY is set"
fi

# Install dependencies
echo ""
echo "Installing dependencies..."
pip3 install -q requests pytest python-dotenv 2>/dev/null || pip install -q requests pytest python-dotenv

echo -e "${GREEN}✓${NC} Dependencies installed"

# Test connection
if [ -n "$LEMLIST_API_KEY" ]; then
    echo ""
    echo "Testing API connection..."
    
    if curl -s --user ":$LEMLIST_API_KEY" "https://api.lemlist.com/api/team" > /dev/null; then
        echo -e "${GREEN}✓${NC} API connection successful"
    else
        echo -e "${RED}✗${NC} API connection failed"
        echo "   Please check your API key"
    fi
fi

# Show usage
echo ""
echo "========================================"
echo "Setup complete!"
echo "========================================"
echo ""
echo "Quick start:"
echo ""
echo "1. Set your API key:"
echo "   export LEMLIST_API_KEY='your_api_key_here'"
echo ""
echo "2. Run examples:"
echo "   python3 examples/campaigns.py"
echo "   python3 examples/leads.py"
echo "   python3 examples/inbox.py"
echo ""
echo "3. Run tests:"
echo "   cd tests && python3 -m pytest test_integration_*.py -v"
echo ""
echo "Documentation:"
echo "   docs/authentication.md - Auth guide"
echo "   docs/rate-limits.md    - Rate limiting"
echo "   docs/error-handling.md - Error handling"
echo "   docs/testing.md        - Testing guide"
echo ""
