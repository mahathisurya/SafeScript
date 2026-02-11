#!/bin/bash

# Script to demonstrate EthicaLang examples
# This helps recruiters quickly see the language in action

echo "=========================================="
echo "  EthicaLang - Example Demonstrations"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

run_example() {
    local file=$1
    local description=$2
    local should_pass=$3
    
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}Example: $description${NC}"
    echo -e "${BLUE}File: $file${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    
    if [ "$should_pass" = "pass" ]; then
        python -m ethicalang.cli.main run "$file"
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ Program executed successfully${NC}"
        else
            echo -e "${RED}✗ Unexpected failure${NC}"
        fi
    else
        python -m ethicalang.cli.main check "$file"
        if [ $? -ne 0 ]; then
            echo -e "${GREEN}✓ Program correctly rejected${NC}"
        else
            echo -e "${RED}✗ Program should have been rejected${NC}"
        fi
    fi
    
    echo ""
    echo ""
}

# Check if examples exist
if [ ! -d "examples" ]; then
    echo -e "${RED}Error: examples/ directory not found${NC}"
    echo "Please run this script from the project root directory"
    exit 1
fi

echo "This script demonstrates EthicaLang's static analysis capabilities."
echo "It will run several example programs, both good and bad."
echo ""
read -p "Press Enter to continue..."
echo ""

# Good examples
echo ""
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo -e "${GREEN}  GOOD EXAMPLES (Should Pass)${NC}"
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo ""

run_example "examples/good_simple_calculator.eth" "Simple Calculator" "pass"
run_example "examples/good_data_collection.eth" "Ethical Data Collection" "pass"
run_example "examples/fibonacci.eth" "Fibonacci Sequence" "pass"

# Bad examples
echo ""
echo -e "${RED}════════════════════════════════════════${NC}"
echo -e "${RED}  BAD EXAMPLES (Should Fail)${NC}"
echo -e "${RED}════════════════════════════════════════${NC}"
echo ""

run_example "examples/bad_no_consent.eth" "Missing Consent Annotation" "fail"
run_example "examples/bad_energy_expensive.eth" "Energy Budget Exceeded" "fail"
run_example "examples/bad_poor_readability.eth" "Poor Readability" "fail"
run_example "examples/bad_too_clever.eth" "Overly Clever Code" "fail"

echo ""
echo -e "${BLUE}=========================================="
echo -e "  Demonstration Complete"
echo -e "==========================================${NC}"
echo ""
echo "For more information, see the README.md file"
echo "To run a specific example: python -m ethicalang.cli.main run examples/filename.eth"
echo ""
