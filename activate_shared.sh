#!/bin/bash
# Shared Virtual Environment Activation Script
# Usage: source activate_shared.sh

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Activating Shared Test Environment${NC}"
echo -e "${BLUE}======================================${NC}"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found. Creating...${NC}"
    python3 -m venv .venv --without-pip
    echo -e "${GREEN}✅ Virtual environment created${NC}"
fi

# Activate virtual environment
source .venv/bin/activate

# Check if pip is installed
if ! command -v pip &> /dev/null; then
    echo -e "${YELLOW}⚠️  pip not found. Installing...${NC}"
    curl https://bootstrap.pypa.io/get-pip.py | python
    echo -e "${GREEN}✅ pip installed${NC}"
fi

# Upgrade pip to latest version
echo -e "${BLUE}📦 Upgrading pip...${NC}"
pip install --upgrade pip

# Display environment info
echo -e "${GREEN}✅ Shared environment activated!${NC}"
echo -e "${BLUE}📍 Virtual Environment:${NC} $(which python)"
echo -e "${BLUE}🐍 Python Version:${NC} $(python --version)"
echo -e "${BLUE}📦 Pip Version:${NC} $(pip --version)"
echo ""
echo -e "${BLUE}Available commands:${NC}"
echo -e "  ${GREEN}install-deps${NC}     - Install all dependencies"
echo -e "  ${GREEN}install-dev${NC}      - Install development dependencies"
echo -e "  ${GREEN}install-test${NC}     - Install testing dependencies"
echo -e "  ${GREEN}run-tests${NC}        - Run all tests"
echo -e "  ${GREEN}run-linting${NC}      - Run code linting"
echo -e "  ${GREEN}deactivate${NC}       - Exit virtual environment"
echo ""

# Create aliases for convenience
alias install-deps='pip install -r requirements.txt'
alias install-dev='pip install -r requirements-dev.txt'
alias install-test='pip install -r requirements-test.txt'
alias run-tests='python test_runner.py'
alias run-linting='flake8 NewsX/ && black --check NewsX/'

echo -e "${YELLOW}💡 Tip: Use 'install-deps' to install core dependencies${NC}"