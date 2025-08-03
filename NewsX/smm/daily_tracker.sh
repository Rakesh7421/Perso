#!/bin/bash

# SMM Tool Daily Tracker Script
# Quick commands for daily project management

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project paths
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TRACKER_SCRIPT="$PROJECT_DIR/project_tracker.py"

# Helper functions
print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  SMM Tool Daily Tracker${NC}"
    echo -e "${BLUE}  $(date '+%Y-%m-%d %H:%M:%S')${NC}"
    echo -e "${BLUE}================================${NC}"
    echo
}

print_section() {
    echo -e "${YELLOW}📋 $1${NC}"
    echo "----------------------------"
}

# Main functions
show_status() {
    print_header
    print_section "Current Progress"
    
    if [ -f "$TRACKER_SCRIPT" ]; then
        python3 "$TRACKER_SCRIPT" status
    else
        echo -e "${RED}❌ Tracker script not found${NC}"
    fi
    echo
}

show_today_tasks() {
    print_section "Today's Focus"
    
    if [ -f "$PROJECT_DIR/WEEKLY_PROGRESS_TRACKER.md" ]; then
        # Extract today's tasks from weekly tracker
        DAY_OF_WEEK=$(date '+%A')
        echo "📅 $DAY_OF_WEEK Tasks:"
        grep -A 10 "#### $DAY_OF_WEEK Tasks" "$PROJECT_DIR/WEEKLY_PROGRESS_TRACKER.md" | \
        grep "- \[ \]" | head -5 | sed 's/^/  /'
    else
        echo -e "${YELLOW}⚠️  Weekly tracker not found${NC}"
        echo "   Create one with: ./daily_tracker.sh create-weekly"
    fi
    echo
}

quick_standup() {
    print_header
    
    echo -e "${GREEN}🎯 Daily Standup${NC}"
    echo
    
    # Yesterday's achievements
    print_section "Yesterday's Achievements"
    echo "What did you complete yesterday?"
    echo "(Review and update your progress files)"
    echo
    
    # Today's goals
    print_section "Today's Goals"
    show_today_tasks
    
    # Blockers
    print_section "Any Blockers?"
    echo "Check your weekly tracker for logged issues"
    echo
    
    # Quick status
    show_status
}

create_weekly() {
    print_header
    print_section "Creating Weekly Tracker"
    
    if [ -f "$TRACKER_SCRIPT" ]; then
        python3 "$TRACKER_SCRIPT" weekly
        echo -e "${GREEN}✅ Weekly tracker created${NC}"
    else
        WEEK_NUM=$(date '+%V')
        cp "$PROJECT_DIR/WEEKLY_PROGRESS_TRACKER.md" "$PROJECT_DIR/WEEKLY_PROGRESS_TRACKER_W$WEEK_NUM.md"
        echo -e "${GREEN}✅ Weekly tracker copied manually${NC}"
    fi
    echo
}

mark_task_done() {
    if [ -z "$1" ]; then
        echo -e "${RED}❌ Please provide a task description${NC}"
        echo "Usage: ./daily_tracker.sh done \"Task description\""
        return 1
    fi
    
    print_section "Marking Task Complete"
    
    if [ -f "$TRACKER_SCRIPT" ]; then
        python3 "$TRACKER_SCRIPT" update "$1" --completed
        echo -e "${GREEN}✅ Task marked as complete${NC}"
    else
        echo -e "${YELLOW}⚠️  Manual update needed in tracking files${NC}"
    fi
    echo
}

generate_report() {
    print_header
    print_section "Generating Status Report"
    
    if [ -f "$TRACKER_SCRIPT" ]; then
        python3 "$TRACKER_SCRIPT" report > "status_report_$(date '+%Y%m%d').md"
        echo -e "${GREEN}✅ Report generated: status_report_$(date '+%Y%m%d').md${NC}"
    else
        echo -e "${RED}❌ Cannot generate automated report${NC}"
    fi
    echo
}

backup_progress() {
    print_section "Backing Up Progress"
    
    BACKUP_DIR="$PROJECT_DIR/backups/$(date '+%Y%m%d')"
    mkdir -p "$BACKUP_DIR"
    
    # Backup tracking files
    cp "$PROJECT_DIR/SMM_TOOL_DEVELOPMENT_PLAN.md" "$BACKUP_DIR/" 2>/dev/null
    cp "$PROJECT_DIR/WEEKLY_PROGRESS_TRACKER"*.md "$BACKUP_DIR/" 2>/dev/null
    cp "$PROJECT_DIR/project_config.json" "$BACKUP_DIR/" 2>/dev/null
    
    echo -e "${GREEN}✅ Progress backed up to $BACKUP_DIR${NC}"
    echo
}

show_velocity() {
    print_section "Development Velocity"
    
    if [ -f "$TRACKER_SCRIPT" ]; then
        python3 "$TRACKER_SCRIPT" velocity
    else
        echo -e "${YELLOW}⚠️  Velocity tracking requires automation script${NC}"
    fi
    echo
}

open_files() {
    print_section "Opening Project Files"
    
    # Try to open files with VS Code if available
    if command -v code &> /dev/null; then
        code "$PROJECT_DIR/SMM_TOOL_DEVELOPMENT_PLAN.md"
        code "$PROJECT_DIR/WEEKLY_PROGRESS_TRACKER.md"
        echo -e "${GREEN}✅ Files opened in VS Code${NC}"
    else
        echo -e "${YELLOW}⚠️  VS Code not found. Open these files manually:${NC}"
        echo "   - SMM_TOOL_DEVELOPMENT_PLAN.md"
        echo "   - WEEKLY_PROGRESS_TRACKER.md"
    fi
    echo
}

show_help() {
    print_header
    echo -e "${GREEN}Available Commands:${NC}"
    echo
    echo -e "${BLUE}./daily_tracker.sh status${NC}        - Show current progress"
    echo -e "${BLUE}./daily_tracker.sh standup${NC}       - Quick daily standup"
    echo -e "${BLUE}./daily_tracker.sh today${NC}         - Show today's tasks"
    echo -e "${BLUE}./daily_tracker.sh done \"task\"${NC}    - Mark task as complete"
    echo -e "${BLUE}./daily_tracker.sh report${NC}        - Generate status report"
    echo -e "${BLUE}./daily_tracker.sh create-weekly${NC} - Create new weekly tracker"
    echo -e "${BLUE}./daily_tracker.sh backup${NC}        - Backup progress files"
    echo -e "${BLUE}./daily_tracker.sh velocity${NC}      - Show development velocity"
    echo -e "${BLUE}./daily_tracker.sh open${NC}          - Open tracking files"
    echo -e "${BLUE}./daily_tracker.sh help${NC}          - Show this help message"
    echo
    echo -e "${YELLOW}Examples:${NC}"
    echo '  ./daily_tracker.sh done "Project Structure Setup"'
    echo '  ./daily_tracker.sh standup'
    echo '  ./daily_tracker.sh status'
    echo
}

# Main script logic
case "$1" in
    "status")
        show_status
        ;;
    "standup")
        quick_standup
        ;;
    "today")
        print_header
        show_today_tasks
        ;;
    "done")
        mark_task_done "$2"
        ;;
    "report")
        generate_report
        ;;
    "create-weekly")
        create_weekly
        ;;
    "backup")
        backup_progress
        ;;
    "velocity")
        print_header
        show_velocity
        ;;
    "open")
        open_files
        ;;
    "help"|"--help"|"-h")
        show_help
        ;;
    "")
        # Default: show standup
        quick_standup
        ;;
    *)
        echo -e "${RED}❌ Unknown command: $1${NC}"
        echo "Use './daily_tracker.sh help' to see available commands"
        exit 1
        ;;
esac

# End with a helpful tip
if [ "$1" != "help" ] && [ "$1" != "--help" ] && [ "$1" != "-h" ]; then
    echo -e "${BLUE}💡 Tip: Run './daily_tracker.sh help' to see all available commands${NC}"
fi