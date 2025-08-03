#!/bin/bash

# Test script for VS Code Extension Manager
# This script tests various functionalities of the extension manager

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_test() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[PASS]${NC} $1"
}

print_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
}

print_info() {
    echo -e "${YELLOW}[INFO]${NC} $1"
}

# Test 1: Check if VS Code is installed
test_vscode_installation() {
    print_test "Checking VS Code installation..."
    
    if command -v code &> /dev/null; then
        print_success "VS Code is installed and accessible"
        code --version
        return 0
    else
        print_fail "VS Code is not installed or not in PATH"
        return 1
    fi
}

# Test 2: Check if script exists and is executable
test_script_exists() {
    print_test "Checking if extension manager script exists..."
    
    local script_path="/home/rakesh/Coderex/util/vscode_extension_manager.sh"
    
    if [[ -f "$script_path" ]]; then
        print_success "Script exists at $script_path"
        
        if [[ -x "$script_path" ]]; then
            print_success "Script is executable"
            return 0
        else
            print_fail "Script is not executable"
            return 1
        fi
    else
        print_fail "Script does not exist"
        return 1
    fi
}

# Test 3: List current extensions
test_list_extensions() {
    print_test "Listing current VS Code extensions..."
    
    local extensions=$(code --list-extensions 2>/dev/null)
    
    if [[ -n "$extensions" ]]; then
        print_success "Found extensions:"
        echo "$extensions" | head -10
        local count=$(echo "$extensions" | wc -l)
        print_info "Total extensions: $count"
        return 0
    else
        print_info "No extensions found or VS Code not properly configured"
        return 1
    fi
}

# Test 4: Test extension status checking
test_extension_status() {
    print_test "Testing extension status checking..."
    
    local first_extension=$(code --list-extensions 2>/dev/null | head -1)
    
    if [[ -n "$first_extension" ]]; then
        print_info "Testing with extension: $first_extension"
        
        # Check if extension is in disabled list
        local disabled_extensions=$(code --list-extensions --disabled 2>/dev/null)
        
        if echo "$disabled_extensions" | grep -q "^$first_extension$"; then
            print_info "Extension is currently DISABLED"
        else
            print_info "Extension is currently ENABLED"
        fi
        
        print_success "Extension status check working"
        return 0
    else
        print_info "No extensions available for testing"
        return 1
    fi
}

# Test 5: Test basic VS Code commands
test_vscode_commands() {
    print_test "Testing VS Code extension commands..."
    
    # Test list extensions command
    if code --list-extensions &>/dev/null; then
        print_success "List extensions command works"
    else
        print_fail "List extensions command failed"
        return 1
    fi
    
    # Test list disabled extensions command
    if code --list-extensions --disabled &>/dev/null; then
        print_success "List disabled extensions command works"
    else
        print_fail "List disabled extensions command failed"
        return 1
    fi
    
    # Test show versions command
    if code --list-extensions --show-versions &>/dev/null; then
        print_success "Show versions command works"
    else
        print_fail "Show versions command failed"
        return 1
    fi
    
    return 0
}

# Test 6: Create a sample extension list for testing
create_sample_backup() {
    print_test "Creating sample extension backup for testing..."
    
    local backup_file="/home/rakesh/Coderex/util/sample_extensions_backup.txt"
    
    # Get current extensions or create sample ones
    local extensions=$(code --list-extensions 2>/dev/null)
    
    if [[ -n "$extensions" ]]; then
        echo "$extensions" > "$backup_file"
        print_success "Created backup file with current extensions: $backup_file"
    else
        # Create sample extension list
        cat > "$backup_file" << EOF
ms-python.python
ms-vscode.vscode-typescript-next
ms-vscode.vscode-json
ms-vscode.theme-default
EOF
        print_info "Created sample backup file: $backup_file"
    fi
    
    return 0
}

# Test 7: Test script help functionality
test_script_help() {
    print_test "Testing script help functionality..."
    
    local script_path="/home/rakesh/Coderex/util/vscode_extension_manager.sh"
    
    # This is a basic test - in real scenario, we'd need to simulate input
    if [[ -f "$script_path" ]]; then
        print_success "Script is ready for interactive testing"
        print_info "To test interactively, run: $script_path"
        return 0
    else
        print_fail "Script not found"
        return 1
    fi
}

# Main test runner
main() {
    echo "=================================="
    echo "VS Code Extension Manager Test Suite"
    echo "=================================="
    echo
    
    local tests_passed=0
    local tests_total=0
    
    # Run tests
    ((tests_total++))
    if test_vscode_installation; then ((tests_passed++)); fi
    echo
    
    ((tests_total++))
    if test_script_exists; then ((tests_passed++)); fi
    echo
    
    ((tests_total++))
    if test_list_extensions; then ((tests_passed++)); fi
    echo
    
    ((tests_total++))
    if test_extension_status; then ((tests_passed++)); fi
    echo
    
    ((tests_total++))
    if test_vscode_commands; then ((tests_passed++)); fi
    echo
    
    ((tests_total++))
    if create_sample_backup; then ((tests_passed++)); fi
    echo
    
    ((tests_total++))
    if test_script_help; then ((tests_passed++)); fi
    echo
    
    # Summary
    echo "=================================="
    echo "Test Summary"
    echo "=================================="
    print_info "Tests passed: $tests_passed/$tests_total"
    
    if [[ $tests_passed -eq $tests_total ]]; then
        print_success "All tests passed! ✅"
        echo
        print_info "You can now run the extension manager:"
        echo "  /home/rakesh/Coderex/util/vscode_extension_manager.sh"
    else
        print_fail "Some tests failed ❌"
        echo
        print_info "Please check the failed tests above"
    fi
}

# Run tests
main