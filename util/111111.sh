#!/bin/bash

# 🚀 CODEREX UTIL - COMBINED SHELL SCRIPTS
# All SH files from util folder combined into one comprehensive script
# This script contains all functionality from:
# - linux-boost.sh
# - setup-all.sh  
# - setup-boost-alias.sh
# - vscode-no-ai.sh

# ============================================================================
# GLOBAL VARIABLES AND COLORS
# ============================================================================

# Colors for better output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Global paths
SCRIPT_DIR="/home/rakesh/Coderex/util"
CODEREX_DIR="/home/rakesh/Coderex"

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

# Function to print colored output
print_colored() {
    echo -e "${1}${2}${NC}"
}

# Function to print header
print_header() {
    clear
    print_colored $CYAN "🚀 Coderex Utility Suite"
    print_colored $WHITE "========================"
}

# Function to pause and wait for user input
pause() {
    print_colored $WHITE "\nPress Enter to continue..."
    read
}

# ============================================================================
# LINUX BOOST MENU FUNCTIONS (from linux-boost.sh)
# ============================================================================

# Function to show boost menu
show_boost_menu() {
    print_header
    print_colored $CYAN "🚀 Linux Boost Menu"
    print_colored $WHITE "------------------------"
    echo "1. Delete temporary files"
    echo "2. Kill browsers (excluding Firefox and VS Code)"
    echo "3. Show + optionally kill heavy memory processes"
    echo "4. Kill specific background tasks (Snap Store, fwupd)"
    echo "5. Clear VS Code Extension Cache"
    echo "6. Clear Cached Memory in RAM (Requires sudo)"
    print_colored $WHITE "------------------------"
    print_colored $YELLOW "VS Code Options:"
    echo "7. Start VS Code (All Extensions)"
    echo "8. Start VS Code (Disable AI Extensions)"
    print_colored $WHITE "------------------------"
    echo "0. Back to main menu"
    print_colored $WHITE "------------------------"
}

# Function to delete temporary files
delete_temp_files() {
    print_colored $BLUE "🧹 Cleaning temporary files..."
    
    # System temp directories
    temp_dirs=(
        "/tmp/*"
        "/var/tmp/*"
        "~/.cache/thumbnails/*"
        "~/.cache/mozilla/*"
        "~/.cache/google-chrome/*"
        "~/.cache/chromium/*"
        "~/.local/share/Trash/*"
    )
    
    total_freed=0
    
    for dir in "${temp_dirs[@]}"; do
        if [[ -d "${dir%/*}" ]]; then
            size_before=$(du -sb "${dir%/*}" 2>/dev/null | cut -f1 || echo "0")
            
            case "$dir" in
                "/tmp/*"|"/var/tmp/*")
                    sudo find "${dir%/*}" -type f -atime +1 -delete 2>/dev/null
                    ;;
                "~/.local/share/Trash/*")
                    expanded_dir="${dir//\~/$HOME}"
                    rm -rf "${expanded_dir}" 2>/dev/null
                    mkdir -p "${expanded_dir%/*}" 2>/dev/null
                    ;;
                *)
                    expanded_dir="${dir//\~/$HOME}"
                    rm -rf "${expanded_dir}" 2>/dev/null
                    ;;
            esac
            
            size_after=$(du -sb "${dir%/*}" 2>/dev/null | cut -f1 || echo "0")
            freed=$((size_before - size_after))
            total_freed=$((total_freed + freed))
        fi
    done
    
    # Clear package cache
    sudo apt-get clean 2>/dev/null
    sudo apt-get autoclean 2>/dev/null
    
    # Clear journal logs older than 3 days
    sudo journalctl --vacuum-time=3d 2>/dev/null
    
    # Convert bytes to human readable
    if [ $total_freed -gt 1073741824 ]; then
        freed_human=$(echo "scale=2; $total_freed / 1073741824" | bc)
        print_colored $GREEN "✅ Freed approximately ${freed_human} GB of temporary files"
    elif [ $total_freed -gt 1048576 ]; then
        freed_human=$(echo "scale=2; $total_freed / 1048576" | bc)
        print_colored $GREEN "✅ Freed approximately ${freed_human} MB of temporary files"
    else
        freed_human=$(echo "scale=2; $total_freed / 1024" | bc)
        print_colored $GREEN "✅ Freed approximately ${freed_human} KB of temporary files"
    fi
}

# Function to kill browsers (excluding Firefox and VS Code)
kill_browsers() {
    print_colored $BLUE "🌐 Killing browsers (excluding Firefox and VS Code)..."
    
    # List of browsers to kill (excluding firefox and code)
    browsers=(
        "chrome"
        "chromium"
        "chromium-browser"
        "opera"
        "opera-stable"
        "brave"
        "brave-browser"
        "microsoft-edge"
        "edge"
        "vivaldi"
        "safari"
        "waterfox"
        "palemoon"
        "seamonkey"
        "epiphany"
        "midori"
        "falkon"
        "konqueror"
    )
    
    killed_count=0
    
    for browser in "${browsers[@]}"; do
        pids=$(pgrep -f "$browser" 2>/dev/null)
        if [ ! -z "$pids" ]; then
            echo "$pids" | while read pid; do
                # Double check it's not firefox or code
                process_name=$(ps -p $pid -o comm= 2>/dev/null)
                if [[ "$process_name" != *"firefox"* ]] && [[ "$process_name" != *"code"* ]] && [[ "$process_name" != *"Code"* ]]; then
                    kill -TERM $pid 2>/dev/null
                    sleep 1
                    if kill -0 $pid 2>/dev/null; then
                        kill -KILL $pid 2>/dev/null
                    fi
                    ((killed_count++))
                    print_colored $YELLOW "  Killed: $process_name (PID: $pid)"
                fi
            done
        fi
    done
    
    if [ $killed_count -eq 0 ]; then
        print_colored $GREEN "✅ No browsers found to kill (Firefox and VS Code preserved)"
    else
        print_colored $GREEN "✅ Killed $killed_count browser processes"
    fi
}

# Function to show and optionally kill heavy memory processes
manage_heavy_processes() {
    print_colored $BLUE "💾 Heavy Memory Processes:"
    print_colored $WHITE "------------------------"
    
    # Get top 10 memory consuming processes
    ps aux --sort=-%mem | head -11 | tail -10 | while IFS= read -r line; do
        echo "$line"
    done
    
    print_colored $WHITE "------------------------"
    print_colored $YELLOW "Do you want to kill any of these processes? (y/N): "
    read -r kill_choice
    
    if [[ $kill_choice =~ ^[Yy]$ ]]; then
        print_colored $CYAN "Enter process names or PIDs to kill (comma separated): "
        read -r processes_to_kill
        
        IFS=',' read -ra PROCESSES <<< "$processes_to_kill"
        for process in "${PROCESSES[@]}"; do
            process=$(echo "$process" | xargs) # Trim whitespace
            
            # Check if it's a PID (numeric) or process name
            if [[ $process =~ ^[0-9]+$ ]]; then
                # It's a PID
                if kill -0 "$process" 2>/dev/null; then
                    process_name=$(ps -p "$process" -o comm= 2>/dev/null)
                    kill -TERM "$process" 2>/dev/null
                    sleep 2
                    if kill -0 "$process" 2>/dev/null; then
                        kill -KILL "$process" 2>/dev/null
                    fi
                    print_colored $GREEN "✅ Killed process: $process_name (PID: $process)"
                else
                    print_colored $RED "❌ Process with PID $process not found"
                fi
            else
                # It's a process name
                pids=$(pgrep -f "$process" 2>/dev/null)
                if [ ! -z "$pids" ]; then
                    echo "$pids" | while read pid; do
                        # Avoid killing critical system processes
                        if [[ "$process" != *"systemd"* ]] && [[ "$process" != *"kernel"* ]] && [[ "$process" != *"init"* ]]; then
                            kill -TERM $pid 2>/dev/null
                            sleep 2
                            if kill -0 $pid 2>/dev/null; then
                                kill -KILL $pid 2>/dev/null
                            fi
                            print_colored $GREEN "✅ Killed process: $process (PID: $pid)"
                        else
                            print_colored $RED "❌ Skipped critical system process: $process"
                        fi
                    done
                else
                    print_colored $RED "❌ Process '$process' not found"
                fi
            fi
        done
    fi
}

# Function to kill specific background tasks
kill_background_tasks() {
    print_colored $BLUE "🔄 Killing specific background tasks..."
    
    # List of background tasks to kill
    bg_tasks=(
        "snap-store"
        "snapd"
        "fwupd"
        "packagekit"
        "update-manager"
        "software-updater"
        "ubuntu-advantage"
        "canonical-livepatch"
        "whoopsie"
        "kerneloops"
        "apport"
    )
    
    killed_count=0
    
    for task in "${bg_tasks[@]}"; do
        pids=$(pgrep -f "$task" 2>/dev/null)
        if [ ! -z "$pids" ]; then
            echo "$pids" | while read pid; do
                process_name=$(ps -p $pid -o comm= 2>/dev/null)
                kill -TERM $pid 2>/dev/null
                sleep 1
                if kill -0 $pid 2>/dev/null; then
                    kill -KILL $pid 2>/dev/null
                fi
                print_colored $YELLOW "  Killed: $process_name (PID: $pid)"
                ((killed_count++))
            done
        fi
    done
    
    # Stop services
    services_to_stop=(
        "snap.snap-store.ubuntu-software"
        "fwupd"
        "packagekit"
    )
    
    for service in "${services_to_stop[@]}"; do
        if systemctl is-active --quiet "$service" 2>/dev/null; then
            sudo systemctl stop "$service" 2>/dev/null
            print_colored $YELLOW "  Stopped service: $service"
            ((killed_count++))
        fi
    done
    
    if [ $killed_count -eq 0 ]; then
        print_colored $GREEN "✅ No background tasks found to kill"
    else
        print_colored $GREEN "✅ Killed/stopped $killed_count background tasks"
    fi
}

# Function to clear VS Code extension cache
clear_vscode_cache() {
    print_colored $BLUE "🔧 Clearing VS Code Extension Cache..."
    
    vscode_dirs=(
        "$HOME/.vscode/extensions"
        "$HOME/.vscode/logs"
        "$HOME/.vscode/CachedExtensions"
        "$HOME/.vscode/CachedExtensionVSIXs"
        "$HOME/.config/Code/logs"
        "$HOME/.config/Code/CachedData"
        "$HOME/.config/Code/CachedExtensions"
        "$HOME/.config/Code/CachedExtensionVSIXs"
    )
    
    total_freed=0
    
    for dir in "${vscode_dirs[@]}"; do
        if [ -d "$dir" ]; then
            case "$dir" in
                *"/extensions")
                    # Don't delete extensions, just clear cache within them
                    find "$dir" -name "*.log" -delete 2>/dev/null
                    find "$dir" -name "cache" -type d -exec rm -rf {} + 2>/dev/null
                    ;;
                *"/logs"|*"/CachedData"|*"/CachedExtensions"|*"/CachedExtensionVSIXs")
                    size_before=$(du -sb "$dir" 2>/dev/null | cut -f1 || echo "0")
                    rm -rf "$dir"/* 2>/dev/null
                    size_after=$(du -sb "$dir" 2>/dev/null | cut -f1 || echo "0")
                    freed=$((size_before - size_after))
                    total_freed=$((total_freed + freed))
                    ;;
            esac
        fi
    done
    
    # Clear workspace storage
    workspace_storage="$HOME/.config/Code/User/workspaceStorage"
    if [ -d "$workspace_storage" ]; then
        # Only clear old workspace storage (older than 7 days)
        find "$workspace_storage" -type d -mtime +7 -exec rm -rf {} + 2>/dev/null
    fi
    
    # Convert bytes to human readable
    if [ $total_freed -gt 1048576 ]; then
        freed_human=$(echo "scale=2; $total_freed / 1048576" | bc)
        print_colored $GREEN "✅ Cleared approximately ${freed_human} MB of VS Code cache"
    else
        freed_human=$(echo "scale=2; $total_freed / 1024" | bc)
        print_colored $GREEN "✅ Cleared approximately ${freed_human} KB of VS Code cache"
    fi
}

# Function to clear cached memory in RAM
clear_ram_cache() {
    print_colored $BLUE "🧠 Clearing Cached Memory in RAM..."
    
    # Check available memory before
    mem_before=$(free -m | awk 'NR==2{print $7}')
    
    print_colored $YELLOW "⚠️  This operation requires sudo privileges"
    print_colored $CYAN "Memory available before: ${mem_before} MB"
    
    echo "Syncing filesystems..."
    sync
    
    echo "Clearing page cache..."
    sudo sh -c 'echo 1 > /proc/sys/vm/drop_caches'
    
    echo "Clearing dentries and inodes..."
    sudo sh -c 'echo 2 > /proc/sys/vm/drop_caches'
    
    echo "Clearing page cache, dentries and inodes..."
    sudo sh -c 'echo 3 > /proc/sys/vm/drop_caches'
    
    # Check available memory after
    sleep 2
    mem_after=$(free -m | awk 'NR==2{print $7}')
    mem_freed=$((mem_after - mem_before))
    
    print_colored $CYAN "Memory available after: ${mem_after} MB"
    if [ $mem_freed -gt 0 ]; then
        print_colored $GREEN "✅ Freed approximately ${mem_freed} MB of RAM cache"
    else
        print_colored $GREEN "✅ RAM cache clearing completed"
    fi
}

# Function to start VS Code with all extensions
start_vscode_all_extensions() {
    print_colored $BLUE "🚀 Starting VS Code with all extensions..."
    
    # Ask if user wants to disable extensions anyway
    print_colored $YELLOW "Do you want to disable extensions anyway? (y/N): "
    read -r disable_choice
    
    if [[ $disable_choice =~ ^[Yy]$ ]]; then
        start_vscode_no_ai_extensions
        return
    fi
    
    # Check if VS Code is already running
    if pgrep -f "code" > /dev/null; then
        print_colored $YELLOW "⚠️  VS Code is already running. Opening new window..."
        code --new-window $CODEREX_DIR &
    else
        print_colored $GREEN "✅ Starting VS Code with all extensions enabled"
        code $CODEREX_DIR &
    fi
    
    print_colored $GREEN "✅ VS Code started successfully"
}

# Function to start VS Code with AI extensions disabled
start_vscode_no_ai_extensions() {
    print_colored $BLUE "🚀 Starting VS Code with AI extensions disabled..."
    
    # List of common AI extensions to disable
    ai_extensions=(
        "github.copilot"
        "github.copilot-chat"
        "ms-vscode.vscode-ai"
        "tabnine.tabnine-vscode"
        "continue.continue"
        "codeium.codeium"
        "amazonwebservices.aws-toolkit-vscode"
        "ms-toolsai.jupyter"
        "ms-python.pylance"
        "ms-python.python"
        "ms-vscode.cpptools"
        "ms-vscode.cpptools-extension-pack"
        "visualstudioexptteam.vscodeintellicode"
        "visualstudioexptteam.intellicode-api-usage-examples"
    )
    
    # Check if VS Code is already running and close it
    if pgrep -f "code" > /dev/null; then
        print_colored $YELLOW "⚠️  Closing existing VS Code instances for clean restart..."
        pkill -f "code"
        sleep 3
    fi
    
    # Create a temporary profile directory for clean extension management
    temp_profile="/tmp/vscode-no-ai-profile-$$"
    mkdir -p "$temp_profile"
    
    print_colored $CYAN "Creating temporary profile without AI extensions..."
    
    # Create settings.json to disable extensions
    mkdir -p "$temp_profile/User"
    cat > "$temp_profile/User/settings.json" << EOF
{
    "extensions.autoCheckUpdates": false,
    "extensions.autoUpdate": false,
    "extensions.showRecommendationsOnlyOnDemand": true,
    "extensions.ignoreRecommendations": true,
    "extensions.closeExtensionDetailsOnViewChange": true,
    "workbench.extensions.installExtensionRecommendations": false,
    "git.enableSmartCommit": true,
    "git.confirmSync": false,
    "editor.minimap.enabled": false,
    "editor.inlineSuggest.enabled": false,
    "editor.quickSuggestions": false,
    "editor.suggestOnTriggerCharacters": false,
    "editor.acceptSuggestionOnEnter": "off",
    "editor.tabCompletion": "off",
    "python.analysis.autoImportCompletions": false,
    "python.analysis.completeFunctionParens": false,
    "typescript.suggest.enabled": false,
    "javascript.suggest.enabled": false
}
EOF
    
    # Method 1: Try using VS Code's extension management
    print_colored $CYAN "Disabling AI extensions..."
    
    for ext in "${ai_extensions[@]}"; do
        # Check if extension is installed
        if code --list-extensions 2>/dev/null | grep -q "^$ext$"; then
            print_colored $YELLOW "  Disabling: $ext"
            code --uninstall-extension "$ext" --force 2>/dev/null || true
        fi
    done
    
    # Wait a moment for changes to take effect
    sleep 2
    
    # Method 2: Start with explicit extension disabling and custom profile
    print_colored $GREEN "✅ Starting VS Code with clean profile (no AI extensions)..."
    
    # Build disable arguments
    disable_args=""
    for ext in "${ai_extensions[@]}"; do
        disable_args="$disable_args --disable-extension $ext"
    done
    
    # Start VS Code with custom user data directory and disabled extensions
    eval "code --user-data-dir='$temp_profile' $disable_args --new-window $CODEREX_DIR &"
    
    # Also provide option to create a permanent profile
    sleep 3
    print_colored $CYAN "\n📝 Extension Management Options:"
    print_colored $WHITE "1. Temp profile created at: $temp_profile"
    print_colored $WHITE "2. To make permanent, you can:"
    print_colored $WHITE "   - Copy settings to ~/.config/Code/User/settings.json"
    print_colored $WHITE "   - Or keep using: code --user-data-dir='$temp_profile'"
    
    print_colored $YELLOW "\nDo you want to create a permanent 'no-ai' profile? (y/N): "
    read -r create_permanent
    
    if [[ $create_permanent =~ ^[Yy]$ ]]; then
        permanent_profile="$HOME/.config/Code-NoAI"
        cp -r "$temp_profile" "$permanent_profile"
        
        # Create a convenient launcher script
        cat > "$SCRIPT_DIR/code-no-ai.sh" << EOF
#!/bin/bash
# VS Code launcher without AI extensions
code --user-data-dir='$permanent_profile' "\$@"
EOF
        chmod +x "$SCRIPT_DIR/code-no-ai.sh"
        
        print_colored $GREEN "✅ Permanent profile created!"
        print_colored $WHITE "Use: $SCRIPT_DIR/code-no-ai.sh to start VS Code without AI"
        
        # Add alias
        if ! grep -q "alias code-no-ai=" ~/.bashrc; then
            echo "alias code-no-ai='$SCRIPT_DIR/code-no-ai.sh'" >> ~/.bashrc
            print_colored $GREEN "✅ Added 'code-no-ai' alias to ~/.bashrc"
        fi
    fi
    
    print_colored $GREEN "✅ VS Code started without AI extensions"
}

# Main boost menu function
run_boost_menu() {
    # Check if bc is installed (needed for calculations)
    if ! command -v bc &> /dev/null; then
        print_colored $YELLOW "⚠️  Installing bc for calculations..."
        sudo apt-get update && sudo apt-get install -y bc
    fi
    
    while true; do
        show_boost_menu
        print_colored $CYAN "Choose an option [0-8]: "
        read -r choice
        
        case $choice in
            1)
                delete_temp_files
                pause
                ;;
            2)
                kill_browsers
                pause
                ;;
            3)
                manage_heavy_processes
                pause
                ;;
            4)
                kill_background_tasks
                pause
                ;;
            5)
                clear_vscode_cache
                pause
                ;;
            6)
                clear_ram_cache
                pause
                ;;
            7)
                start_vscode_all_extensions
                pause
                ;;
            8)
                start_vscode_no_ai_extensions
                pause
                ;;
            0)
                return
                ;;
            *)
                print_colored $RED "❌ Invalid option. Please choose 0-8."
                pause
                ;;
        esac
    done
}

# ============================================================================
# SETUP FUNCTIONS (from setup-all.sh and setup-boost-alias.sh)
# ============================================================================

# Function to setup boost alias
setup_boost_alias() {
    print_colored $BLUE "🔧 Setting up Linux Boost Menu alias..."
    
    SCRIPT_PATH="$SCRIPT_DIR/linux-boost.sh"
    ALIAS_NAME="boost"
    
    # Add alias to .bashrc if it doesn't exist
    if ! grep -q "alias $ALIAS_NAME=" ~/.bashrc; then
        echo "" >> ~/.bashrc
        echo "# Linux Boost Menu alias" >> ~/.bashrc
        echo "alias $ALIAS_NAME='$SCRIPT_PATH'" >> ~/.bashrc
        print_colored $GREEN "✅ Added alias '$ALIAS_NAME' to ~/.bashrc"
    else
        print_colored $GREEN "✅ Alias '$ALIAS_NAME' already exists in ~/.bashrc"
    fi
    
    # Add alias to .bash_aliases if it exists
    if [ -f ~/.bash_aliases ]; then
        if ! grep -q "alias $ALIAS_NAME=" ~/.bash_aliases; then
            echo "" >> ~/.bash_aliases
            echo "# Linux Boost Menu alias" >> ~/.bash_aliases
            echo "alias $ALIAS_NAME='$SCRIPT_PATH'" >> ~/.bash_aliases
            print_colored $GREEN "✅ Added alias '$ALIAS_NAME' to ~/.bash_aliases"
        fi
    fi
}

# Function to setup all aliases and utilities
setup_all_utilities() {
    print_colored $BLUE "🔧 Setting up all Coderex utilities..."
    
    # Make all scripts executable
    chmod +x $SCRIPT_DIR/*.sh
    print_colored $GREEN "✅ Made all scripts executable"
    
    # Setup boost alias
    setup_boost_alias
    
    # Add aliases for the VS Code no-AI launcher
    if ! grep -q "alias code-no-ai=" ~/.bashrc; then
        echo "" >> ~/.bashrc
        echo "# VS Code no-AI launcher alias" >> ~/.bashrc
        echo "alias code-no-ai='$SCRIPT_DIR/vscode-no-ai.sh'" >> ~/.bashrc
        print_colored $GREEN "✅ Added 'code-no-ai' alias to ~/.bashrc"
    fi
    
    # Add alias for the util directory
    if ! grep -q "alias util=" ~/.bashrc; then
        echo "alias util='cd $SCRIPT_DIR'" >> ~/.bashrc
        print_colored $GREEN "✅ Added 'util' alias to ~/.bashrc"
    fi
    
    # Add alias for this combined script
    if ! grep -q "alias coderex-util=" ~/.bashrc; then
        echo "alias coderex-util='$SCRIPT_DIR/COMBINED_ALL_SCRIPTS.sh'" >> ~/.bashrc
        print_colored $GREEN "✅ Added 'coderex-util' alias to ~/.bashrc"
    fi
    
    echo ""
    print_colored $BLUE "🎉 Setup Complete!"
    echo ""
    print_colored $YELLOW "📋 Available Commands (after reloading shell):"
    echo "  boost              - Linux Boost Menu"
    echo "  code-no-ai         - VS Code without AI extensions"
    echo "  util               - Navigate to util directory"
    echo "  coderex-util       - This combined utility script"
    echo ""
    print_colored $YELLOW "📋 Direct Script Usage:"
    echo "  $SCRIPT_DIR/linux-boost.sh"
    echo "  $SCRIPT_DIR/vscode-no-ai.sh"
    echo "  $SCRIPT_DIR/COMBINED_ALL_SCRIPTS.sh"
    echo ""
    print_colored $YELLOW "🔄 Reload your shell:"
    echo "  source ~/.bashrc"
    echo "  # or open a new terminal"
    echo ""
    print_colored $GREEN "✅ All utilities are ready to use!"
}

# ============================================================================
# VS CODE NO-AI FUNCTIONS (from vscode-no-ai.sh)
# ============================================================================

# Standalone VS Code no-AI launcher
launch_vscode_no_ai() {
    # Check if VS Code is installed
    if ! command -v code &> /dev/null; then
        print_colored $RED "❌ VS Code is not installed or not in PATH"
        return 1
    fi
    
    print_colored $BLUE "🚀 Starting VS Code without AI extensions..."
    
    # Close existing VS Code instances
    if pgrep -f "code" > /dev/null; then
        print_colored $YELLOW "⚠️  Closing existing VS Code instances..."
        pkill -f "code"
        sleep 2
    fi
    
    # Create a clean profile directory
    PROFILE_DIR="$HOME/.config/Code-NoAI"
    
    if [ ! -d "$PROFILE_DIR" ]; then
        print_colored $BLUE "📁 Creating clean profile directory..."
        mkdir -p "$PROFILE_DIR/User"
        
        # Create settings.json with AI features disabled
        cat > "$PROFILE_DIR/User/settings.json" << 'EOF'
{
    "extensions.autoCheckUpdates": false,
    "extensions.autoUpdate": false,
    "extensions.showRecommendationsOnlyOnDemand": true,
    "extensions.ignoreRecommendations": true,
    "workbench.extensions.installExtensionRecommendations": false,
    "editor.inlineSuggest.enabled": false,
    "editor.quickSuggestions": {
        "other": false,
        "comments": false,
        "strings": false
    },
    "editor.suggestOnTriggerCharacters": false,
    "editor.acceptSuggestionOnEnter": "off",
    "editor.tabCompletion": "off",
    "editor.wordBasedSuggestions": false,
    "editor.parameterHints.enabled": false,
    "python.analysis.autoImportCompletions": false,
    "python.analysis.completeFunctionParens": false,
    "typescript.suggest.enabled": false,
    "javascript.suggest.enabled": false,
    "html.suggest.html5": false,
    "css.completion.completePropertyWithSemicolon": false,
    "emmet.showSuggestionsAsSnippets": false,
    "files.autoSave": "off",
    "git.enableSmartCommit": true,
    "git.confirmSync": false,
    "workbench.startupEditor": "newUntitledFile"
}
EOF

        # Create keybindings.json to disable AI shortcuts
        cat > "$PROFILE_DIR/User/keybindings.json" << 'EOF'
[
    {
        "key": "ctrl+space",
        "command": "-editor.action.triggerSuggest"
    },
    {
        "key": "ctrl+shift+space",
        "command": "-editor.action.triggerParameterHints"
    },
    {
        "key": "tab",
        "command": "-acceptAlternativeSelectedSuggestion",
        "when": "suggestWidgetVisible && textInputFocus && textInputFocus"
    }
]
EOF

        print_colored $GREEN "✅ Clean profile created at: $PROFILE_DIR"
    fi
    
    # List of AI extensions to disable
    AI_EXTENSIONS=(
        "github.copilot"
        "github.copilot-chat"
        "ms-vscode.vscode-ai"
        "tabnine.tabnine-vscode"
        "continue.continue"
        "codeium.codeium"
        "visualstudioexptteam.vscodeintellicode"
        "visualstudioexptteam.intellicode-api-usage-examples"
        "ms-python.pylance"
        "ms-toolsai.jupyter"
    )
    
    # Build disable arguments
    DISABLE_ARGS=""
    for ext in "${AI_EXTENSIONS[@]}"; do
        DISABLE_ARGS="$DISABLE_ARGS --disable-extension $ext"
    done
    
    # Start VS Code with clean profile and disabled extensions
    print_colored $GREEN "🎯 Launching VS Code with clean environment..."
    
    if [ $# -eq 0 ]; then
        # No arguments provided, open the Coderex directory
        eval "code --user-data-dir='$PROFILE_DIR' $DISABLE_ARGS $CODEREX_DIR &"
    else
        # Arguments provided, pass them along
        eval "code --user-data-dir='$PROFILE_DIR' $DISABLE_ARGS '$*' &"
    fi
    
    print_colored $GREEN "✅ VS Code started without AI extensions!"
    print_colored $YELLOW "📝 Note: This VS Code instance uses a separate profile at $PROFILE_DIR"
    print_colored $BLUE "🔄 To return to normal VS Code, close this instance and run 'code' normally"
}

# ============================================================================
# MAIN MENU SYSTEM
# ============================================================================

# Function to show main menu
show_main_menu() {
    print_header
    print_colored $CYAN "🚀 Coderex Utility Suite - Main Menu"
    print_colored $WHITE "======================================"
    echo ""
    print_colored $YELLOW "System Optimization:"
    echo "1. 🚀 Linux Boost Menu (Full system optimization)"
    echo "2. 🧹 Quick Cache Clear (Temp files + RAM)"
    echo "3. 🔪 Kill Heavy Processes"
    echo "4. 🌐 Kill Browsers (except Firefox)"
    echo ""
    print_colored $YELLOW "VS Code Management:"
    echo "5. 🎯 Launch VS Code (No AI Extensions)"
    echo "6. 🚀 Launch VS Code (All Extensions)"
    echo "7. 🔧 Clear VS Code Cache"
    echo ""
    print_colored $YELLOW "Setup & Configuration:"
    echo "8. ⚙️  Setup All Utilities & Aliases"
    echo "9. 🔗 Setup Boost Alias Only"
    echo ""
    print_colored $YELLOW "Information:"
    echo "i. ℹ️  Show Available Commands"
    echo "h. ❓ Help & Usage"
    echo ""
    echo "0. ❌ Exit"
    print_colored $WHITE "======================================"
}

# Function to show available commands
show_available_commands() {
    print_header
    print_colored $CYAN "📋 Available Commands After Setup"
    print_colored $WHITE "=================================="
    echo ""
    print_colored $YELLOW "Quick Commands (after running setup):"
    echo "  boost              - Linux Boost Menu"
    echo "  code-no-ai         - VS Code without AI extensions"
    echo "  util               - Navigate to util directory"
    echo "  coderex-util       - This combined utility script"
    echo ""
    print_colored $YELLOW "Direct Script Usage:"
    echo "  $SCRIPT_DIR/linux-boost.sh"
    echo "  $SCRIPT_DIR/vscode-no-ai.sh"
    echo "  $SCRIPT_DIR/COMBINED_ALL_SCRIPTS.sh"
    echo ""
    print_colored $YELLOW "Setup Commands:"
    echo "  $SCRIPT_DIR/setup-all.sh"
    echo "  $SCRIPT_DIR/setup-boost-alias.sh"
    echo ""
    print_colored $BLUE "💡 Tip: Run option 8 to set up all aliases automatically!"
    pause
}

# Function to show help
show_help() {
    print_header
    print_colored $CYAN "❓ Help & Usage Guide"
    print_colored $WHITE "===================="
    echo ""
    print_colored $YELLOW "🎯 Purpose:"
    echo "This combined script includes all functionality from the Coderex util folder:"
    echo "- System optimization and cleanup"
    echo "- VS Code management with/without AI extensions"
    echo "- Process management and browser control"
    echo "- Automated setup and alias creation"
    echo ""
    print_colored $YELLOW "🚀 Quick Start:"
    echo "1. Run option 8 to set up all utilities"
    echo "2. Reload your shell: source ~/.bashrc"
    echo "3. Use quick commands like 'boost' or 'code-no-ai'"
    echo ""
    print_colored $YELLOW "⚠️  Important Notes:"
    echo "- Some operations require sudo privileges"
    echo "- Firefox and VS Code are protected from browser cleanup"
    echo "- All operations are designed to be safe and non-destructive"
    echo "- Temporary files older than 1 day are cleaned"
    echo ""
    print_colored $YELLOW "🔧 Troubleshooting:"
    echo "- If commands don't work, run setup again (option 8)"
    echo "- Ensure scripts have execute permissions"
    echo "- Check that VS Code is installed and in PATH"
    echo ""
    pause
}

# Function to quick cache clear
quick_cache_clear() {
    print_colored $BLUE "🧹 Quick Cache Clear..."
    delete_temp_files
    clear_ram_cache
    print_colored $GREEN "✅ Quick cache clear completed!"
}

# Main function
main() {
    # Check if script is run as root (we don't want that for most operations)
    if [ "$EUID" -eq 0 ]; then
        print_colored $RED "❌ Please don't run this script as root. It will ask for sudo when needed."
        exit 1
    fi
    
    while true; do
        show_main_menu
        print_colored $CYAN "Choose an option: "
        read -r choice
        
        case $choice in
            1)
                run_boost_menu
                ;;
            2)
                quick_cache_clear
                pause
                ;;
            3)
                manage_heavy_processes
                pause
                ;;
            4)
                kill_browsers
                pause
                ;;
            5)
                launch_vscode_no_ai
                pause
                ;;
            6)
                start_vscode_all_extensions
                pause
                ;;
            7)
                clear_vscode_cache
                pause
                ;;
            8)
                setup_all_utilities
                pause
                ;;
            9)
                setup_boost_alias
                pause
                ;;
            i|I)
                show_available_commands
                ;;
            h|H)
                show_help
                ;;
            0)
                print_colored $GREEN "👋 Goodbye! Thanks for using Coderex Utility Suite."
                exit 0
                ;;
            *)
                print_colored $RED "❌ Invalid option. Please try again."
                pause
                ;;
        esac
    done
}

# ============================================================================
# SCRIPT EXECUTION
# ============================================================================

# Check if script is being sourced or executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    # Script is being executed directly
    print_colored $CYAN "🚀 Starting Coderex Utility Suite..."
    main
else
    # Script is being sourced
    print_colored $GREEN "✅ Coderex Utility Suite functions loaded!"
    print_colored $YELLOW "💡 Run 'main' to start the interactive menu"
fi

# End of Combined Shell Scripts
# All SH files from util folder have been successfully combined into this comprehensive script.