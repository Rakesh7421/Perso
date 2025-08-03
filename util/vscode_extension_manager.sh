#!/bin/bash

# VS Code Extension Manager
# Interactive script to enable/disable VS Code extensions
# Author: Assistant
# Version: 1.0

# Colors for better UI
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Function to print colored output
print_color() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to print header
print_header() {
    clear
    print_color $CYAN "╔══════════════════════════════════════════════════════════════╗"
    print_color $CYAN "║                VS Code Extension Manager                     ║"
    print_color $CYAN "║              Interactive Extension Control                   ║"
    print_color $CYAN "╚══════════════════════════════════════════════════════════════╝"
    echo
}

# Function to check if VS Code is installed
check_vscode() {
    if ! command -v code &> /dev/null; then
        print_color $RED "❌ VS Code is not installed or not in PATH"
        print_color $YELLOW "Please install VS Code or add it to your PATH"
        exit 1
    fi
    print_color $GREEN "✅ VS Code found"
}

# Function to get all installed extensions
get_installed_extensions() {
    code --list-extensions 2>/dev/null
}

# Function to get extension details
get_extension_details() {
    local extension_id=$1
    local details=$(code --list-extensions --show-versions | grep "^$extension_id@")
    if [[ -n "$details" ]]; then
        echo "$details"
    else
        echo "$extension_id@unknown"
    fi
}

# Function to check if extension is enabled
is_extension_enabled() {
    local extension_id=$1
    local disabled_extensions=$(code --list-extensions --disabled 2>/dev/null)
    
    if echo "$disabled_extensions" | grep -q "^$extension_id$"; then
        return 1  # Extension is disabled
    else
        return 0  # Extension is enabled
    fi
}

# Function to display extensions with status
display_extensions() {
    local extensions=$(get_installed_extensions)
    local counter=1
    
    if [[ -z "$extensions" ]]; then
        print_color $YELLOW "No extensions found"
        return
    fi
    
    print_color $WHITE "📦 Installed Extensions:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    printf "%-4s %-8s %-40s %s\n" "No." "Status" "Extension ID" "Version"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    while IFS= read -r extension; do
        if [[ -n "$extension" ]]; then
            local details=$(get_extension_details "$extension")
            local version=$(echo "$details" | cut -d'@' -f2)
            
            if is_extension_enabled "$extension"; then
                local status="${GREEN}ENABLED${NC}"
            else
                local status="${RED}DISABLED${NC}"
            fi
            
            printf "%-4s %-16s %-40s %s\n" "$counter" "$status" "$extension" "$version"
            ((counter++))
        fi
    done <<< "$extensions"
    echo
}

# Function to enable extension
enable_extension() {
    local extension_id=$1
    print_color $YELLOW "🔄 Enabling extension: $extension_id"
    
    if code --enable-extension "$extension_id" &>/dev/null; then
        print_color $GREEN "✅ Extension enabled successfully"
    else
        print_color $RED "❌ Failed to enable extension"
    fi
}

# Function to disable extension
disable_extension() {
    local extension_id=$1
    print_color $YELLOW "🔄 Disabling extension: $extension_id"
    
    if code --disable-extension "$extension_id" &>/dev/null; then
        print_color $GREEN "✅ Extension disabled successfully"
    else
        print_color $RED "❌ Failed to disable extension"
    fi
}

# Function to toggle extension status
toggle_extension() {
    local extension_id=$1
    
    if is_extension_enabled "$extension_id"; then
        disable_extension "$extension_id"
    else
        enable_extension "$extension_id"
    fi
}

# Function to enable all extensions
enable_all_extensions() {
    local extensions=$(get_installed_extensions)
    local count=0
    
    print_color $YELLOW "🔄 Enabling all extensions..."
    
    while IFS= read -r extension; do
        if [[ -n "$extension" ]]; then
            if ! is_extension_enabled "$extension"; then
                code --enable-extension "$extension" &>/dev/null
                ((count++))
            fi
        fi
    done <<< "$extensions"
    
    print_color $GREEN "✅ Enabled $count extensions"
}

# Function to disable all extensions
disable_all_extensions() {
    local extensions=$(get_installed_extensions)
    local count=0
    
    print_color $YELLOW "🔄 Disabling all extensions..."
    
    while IFS= read -r extension; do
        if [[ -n "$extension" ]]; then
            if is_extension_enabled "$extension"; then
                code --disable-extension "$extension" &>/dev/null
                ((count++))
            fi
        fi
    done <<< "$extensions"
    
    print_color $GREEN "✅ Disabled $count extensions"
}

# Function to search and filter extensions
search_extensions() {
    local search_term=$1
    local extensions=$(get_installed_extensions)
    local counter=1
    local found=false
    
    print_color $WHITE "🔍 Search results for: '$search_term'"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    printf "%-4s %-8s %-40s %s\n" "No." "Status" "Extension ID" "Version"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    while IFS= read -r extension; do
        if [[ -n "$extension" && "$extension" == *"$search_term"* ]]; then
            found=true
            local details=$(get_extension_details "$extension")
            local version=$(echo "$details" | cut -d'@' -f2)
            
            if is_extension_enabled "$extension"; then
                local status="${GREEN}ENABLED${NC}"
            else
                local status="${RED}DISABLED${NC}"
            fi
            
            printf "%-4s %-16s %-40s %s\n" "$counter" "$status" "$extension" "$version"
            ((counter++))
        fi
    done <<< "$extensions"
    
    if [[ "$found" == false ]]; then
        print_color $YELLOW "No extensions found matching '$search_term'"
    fi
    echo
}

# Function to get extension by number
get_extension_by_number() {
    local number=$1
    local extensions=$(get_installed_extensions)
    local counter=1
    
    while IFS= read -r extension; do
        if [[ -n "$extension" ]]; then
            if [[ $counter -eq $number ]]; then
                echo "$extension"
                return
            fi
            ((counter++))
        fi
    done <<< "$extensions"
}

# Function to show extension statistics
show_statistics() {
    local extensions=$(get_installed_extensions)
    local total=0
    local enabled=0
    local disabled=0
    
    while IFS= read -r extension; do
        if [[ -n "$extension" ]]; then
            ((total++))
            if is_extension_enabled "$extension"; then
                ((enabled++))
            else
                ((disabled++))
            fi
        fi
    done <<< "$extensions"
    
    print_color $WHITE "📊 Extension Statistics:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    print_color $CYAN "Total Extensions: $total"
    print_color $GREEN "Enabled: $enabled"
    print_color $RED "Disabled: $disabled"
    echo
}

# Function to backup extension list
backup_extensions() {
    local backup_file="$HOME/vscode_extensions_backup_$(date +%Y%m%d_%H%M%S).txt"
    local extensions=$(get_installed_extensions)
    
    if [[ -n "$extensions" ]]; then
        echo "$extensions" > "$backup_file"
        print_color $GREEN "✅ Extension list backed up to: $backup_file"
    else
        print_color $YELLOW "No extensions to backup"
    fi
}

# Function to install extension from backup
restore_extensions() {
    read -p "Enter backup file path: " backup_file
    
    if [[ ! -f "$backup_file" ]]; then
        print_color $RED "❌ Backup file not found"
        return
    fi
    
    print_color $YELLOW "🔄 Restoring extensions from backup..."
    local count=0
    
    while IFS= read -r extension; do
        if [[ -n "$extension" ]]; then
            print_color $CYAN "Installing: $extension"
            if code --install-extension "$extension" &>/dev/null; then
                ((count++))
            fi
        fi
    done < "$backup_file"
    
    print_color $GREEN "✅ Restored $count extensions"
}

# Function to show help
show_help() {
    print_color $WHITE "📖 Help - Available Commands:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    print_color $CYAN "1-9999    - Toggle extension by number"
    print_color $CYAN "list      - Show all extensions"
    print_color $CYAN "enable    - Enable extension by ID or number"
    print_color $CYAN "disable   - Disable extension by ID or number"
    print_color $CYAN "enable-all - Enable all extensions"
    print_color $CYAN "disable-all - Disable all extensions"
    print_color $CYAN "search    - Search extensions"
    print_color $CYAN "stats     - Show statistics"
    print_color $CYAN "backup    - Backup extension list"
    print_color $CYAN "restore   - Restore from backup"
    print_color $CYAN "help      - Show this help"
    print_color $CYAN "quit/exit - Exit the program"
    echo
}

# Function to handle user input
handle_input() {
    local input=$1
    
    case $input in
        [0-9]*)
            # Handle numeric input (toggle extension)
            local extension=$(get_extension_by_number "$input")
            if [[ -n "$extension" ]]; then
                toggle_extension "$extension"
            else
                print_color $RED "❌ Invalid extension number"
            fi
            ;;
        "list"|"l")
            display_extensions
            ;;
        "enable"|"e")
            read -p "Enter extension ID or number: " ext_input
            if [[ "$ext_input" =~ ^[0-9]+$ ]]; then
                local extension=$(get_extension_by_number "$ext_input")
                if [[ -n "$extension" ]]; then
                    enable_extension "$extension"
                else
                    print_color $RED "❌ Invalid extension number"
                fi
            else
                enable_extension "$ext_input"
            fi
            ;;
        "disable"|"d")
            read -p "Enter extension ID or number: " ext_input
            if [[ "$ext_input" =~ ^[0-9]+$ ]]; then
                local extension=$(get_extension_by_number "$ext_input")
                if [[ -n "$extension" ]]; then
                    disable_extension "$extension"
                else
                    print_color $RED "❌ Invalid extension number"
                fi
            else
                disable_extension "$ext_input"
            fi
            ;;
        "enable-all"|"ea")
            read -p "Are you sure you want to enable all extensions? (y/N): " confirm
            if [[ "$confirm" =~ ^[Yy]$ ]]; then
                enable_all_extensions
            fi
            ;;
        "disable-all"|"da")
            read -p "Are you sure you want to disable all extensions? (y/N): " confirm
            if [[ "$confirm" =~ ^[Yy]$ ]]; then
                disable_all_extensions
            fi
            ;;
        "search"|"s")
            read -p "Enter search term: " search_term
            if [[ -n "$search_term" ]]; then
                search_extensions "$search_term"
            fi
            ;;
        "stats"|"st")
            show_statistics
            ;;
        "backup"|"b")
            backup_extensions
            ;;
        "restore"|"r")
            restore_extensions
            ;;
        "help"|"h"|"?")
            show_help
            ;;
        "quit"|"exit"|"q")
            print_color $GREEN "👋 Goodbye!"
            exit 0
            ;;
        "")
            # Empty input, do nothing
            ;;
        *)
            print_color $RED "❌ Unknown command: $input"
            print_color $YELLOW "Type 'help' for available commands"
            ;;
    esac
}

# Main function
main() {
    # Check if VS Code is installed
    check_vscode
    
    # Main loop
    while true; do
        print_header
        show_statistics
        display_extensions
        show_help
        
        echo -n "$(print_color $PURPLE "Enter command: ")"
        read -r user_input
        
        handle_input "$user_input"
        
        # Pause before next iteration
        echo
        read -p "Press Enter to continue..."
    done
}

# Trap Ctrl+C
trap 'print_color $GREEN "\n👋 Goodbye!"; exit 0' INT

# Run main function
main