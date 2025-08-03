#!/usr/bin/env python3
"""
SMM Tool Project Tracker
Automation script for tracking progress and generating reports
"""

import json
import re
import os
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import argparse

class ProjectTracker:
    def __init__(self, base_path: str = "."):
        self.base_path = base_path
        self.config_file = os.path.join(base_path, "project_config.json")
        self.main_plan_file = os.path.join(base_path, "SMM_TOOL_DEVELOPMENT_PLAN.md")
        self.weekly_tracker_file = os.path.join(base_path, "WEEKLY_PROGRESS_TRACKER.md")
        
    def load_config(self) -> Dict:
        """Load project configuration"""
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Configuration file not found: {self.config_file}")
            return {}
    
    def save_config(self, config: Dict):
        """Save project configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def count_tasks(self, file_path: str) -> Tuple[int, int]:
        """Count total and completed tasks in a markdown file"""
        if not os.path.exists(file_path):
            return 0, 0
            
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Count all checkboxes
        total_tasks = len(re.findall(r'- \[[ x]\]', content))
        completed_tasks = len(re.findall(r'- \[x\]', content))
        
        return total_tasks, completed_tasks
    
    def get_progress_stats(self) -> Dict:
        """Get overall project progress statistics"""
        main_total, main_completed = self.count_tasks(self.main_plan_file)
        weekly_total, weekly_completed = self.count_tasks(self.weekly_tracker_file)
        
        overall_progress = (main_completed / main_total * 100) if main_total > 0 else 0
        weekly_progress = (weekly_completed / weekly_total * 100) if weekly_total > 0 else 0
        
        return {
            "main_plan": {
                "total_tasks": main_total,
                "completed_tasks": main_completed,
                "progress_percentage": round(overall_progress, 1)
            },
            "weekly_tracker": {
                "total_tasks": weekly_total,
                "completed_tasks": weekly_completed,
                "progress_percentage": round(weekly_progress, 1)
            },
            "last_updated": datetime.now().isoformat()
        }
    
    def generate_status_report(self) -> str:
        """Generate a comprehensive status report"""
        config = self.load_config()
        stats = self.get_progress_stats()
        
        report = f"""
# 📊 SMM Tool Project Status Report
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Overall Progress
- **Main Plan Progress**: {stats['main_plan']['completed_tasks']}/{stats['main_plan']['total_tasks']} tasks ({stats['main_plan']['progress_percentage']}%)
- **Weekly Progress**: {stats['weekly_tracker']['completed_tasks']}/{stats['weekly_tracker']['total_tasks']} tasks ({stats['weekly_tracker']['progress_percentage']}%)

## Project Information
- **Project Name**: {config.get('project', {}).get('name', 'N/A')}
- **Version**: {config.get('project', {}).get('version', 'N/A')}
- **Current Phase**: {config.get('project', {}).get('current_phase', 'N/A').title()}
- **Start Date**: {config.get('project', {}).get('start_date', 'N/A')}
- **Estimated Completion**: {config.get('project', {}).get('estimated_completion', 'N/A')}

## Phase Status
"""
        phases = config.get('phases', {})
        for phase_key, phase_data in phases.items():
            status_emoji = {
                'not_started': '⏳',
                'in_progress': '🟡',
                'completed': '✅',
                'blocked': '🔴'
            }.get(phase_data.get('status', 'not_started'), '❓')
            
            report += f"- **{phase_data.get('name', phase_key)}**: {status_emoji} {phase_data.get('status', 'not_started').replace('_', ' ').title()}\n"
        
        report += f"""
## Technology Stack
- **Backend**: {config.get('technology_stack', {}).get('backend', {}).get('framework', 'N/A')}
- **Database**: {config.get('technology_stack', {}).get('backend', {}).get('database', 'N/A')}
- **Deployment**: {config.get('technology_stack', {}).get('infrastructure', {}).get('deployment', 'N/A')}

## Next Actions
"""
        next_actions = config.get('next_actions', [])
        for action in next_actions[:5]:  # Show top 5 actions
            status = action.get('status', 'pending')
            emoji = '✅' if status == 'completed' else '⏳' if status == 'in_progress' else '❌'
            report += f"- {emoji} **{action.get('action', 'N/A')}** (Due: {action.get('due_date', 'N/A')})\n"
        
        return report
    
    def update_progress(self, task_description: str, completed: bool = True):
        """Update a specific task's completion status"""
        files_to_update = [self.main_plan_file, self.weekly_tracker_file]
        
        for file_path in files_to_update:
            if not os.path.exists(file_path):
                continue
                
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Find and update the task
            checkbox_pattern = r'(- \[[ x]\]\s*\*\*.*?' + re.escape(task_description) + r'.*?\*\*.*?)'
            match = re.search(checkbox_pattern, content, re.IGNORECASE)
            
            if match:
                old_line = match.group(1)
                if completed:
                    new_line = old_line.replace('[ ]', '[x]')
                else:
                    new_line = old_line.replace('[x]', '[ ]')
                
                content = content.replace(old_line, new_line)
                
                with open(file_path, 'w') as f:
                    f.write(content)
                
                print(f"Updated task '{task_description}' in {file_path}")
            else:
                print(f"Task '{task_description}' not found in {file_path}")
    
    def create_weekly_tracker(self, week_number: int = None):
        """Create a new weekly tracker file"""
        if week_number is None:
            week_number = datetime.now().isocalendar()[1]
        
        start_date = datetime.now().strftime('%Y-%m-%d')
        end_date = (datetime.now() + timedelta(days=6)).strftime('%Y-%m-%d')
        
        weekly_file = f"WEEKLY_PROGRESS_TRACKER_W{week_number}.md"
        
        # Copy template and update dates
        if os.path.exists(self.weekly_tracker_file):
            with open(self.weekly_tracker_file, 'r') as f:
                template = f.read()
            
            # Replace template variables
            template = template.replace('{{ start_date }}', start_date)
            template = template.replace('{{ end_date }}', end_date)
            template = template.replace('{{ current_date }}', datetime.now().strftime('%Y-%m-%d'))
            template = template.replace('{{ tomorrow_date }}', (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'))
            
            with open(os.path.join(self.base_path, weekly_file), 'w') as f:
                f.write(template)
            
            print(f"Created weekly tracker: {weekly_file}")
        else:
            print("Weekly tracker template not found")
    
    def get_velocity_report(self) -> Dict:
        """Calculate development velocity metrics"""
        stats = self.get_progress_stats()
        config = self.load_config()
        
        start_date = datetime.fromisoformat(config.get('project', {}).get('start_date', datetime.now().isoformat()))
        days_elapsed = (datetime.now() - start_date).days
        
        if days_elapsed > 0:
            tasks_per_day = stats['main_plan']['completed_tasks'] / days_elapsed
            estimated_completion_days = (stats['main_plan']['total_tasks'] - stats['main_plan']['completed_tasks']) / max(tasks_per_day, 0.1)
            estimated_completion_date = datetime.now() + timedelta(days=estimated_completion_days)
        else:
            tasks_per_day = 0
            estimated_completion_date = datetime.now()
        
        return {
            "days_elapsed": days_elapsed,
            "tasks_per_day": round(tasks_per_day, 2),
            "estimated_completion": estimated_completion_date.strftime('%Y-%m-%d'),
            "velocity_trend": "stable"  # This could be calculated from historical data
        }
    
    def export_progress_json(self) -> str:
        """Export progress data as JSON"""
        stats = self.get_progress_stats()
        config = self.load_config()
        velocity = self.get_velocity_report()
        
        export_data = {
            "project_info": config.get('project', {}),
            "progress_stats": stats,
            "velocity_report": velocity,
            "export_timestamp": datetime.now().isoformat()
        }
        
        export_file = f"progress_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        export_path = os.path.join(self.base_path, export_file)
        
        with open(export_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        return export_path

def main():
    parser = argparse.ArgumentParser(description='SMM Tool Project Tracker')
    parser.add_argument('--path', default='.', help='Project base path')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Status command
    subparsers.add_parser('status', help='Show project status')
    
    # Update command
    update_parser = subparsers.add_parser('update', help='Update task completion')
    update_parser.add_argument('task', help='Task description to update')
    update_parser.add_argument('--completed', action='store_true', help='Mark as completed')
    update_parser.add_argument('--incomplete', action='store_true', help='Mark as incomplete')
    
    # Report command
    subparsers.add_parser('report', help='Generate status report')
    
    # Weekly command
    weekly_parser = subparsers.add_parser('weekly', help='Create weekly tracker')
    weekly_parser.add_argument('--week', type=int, help='Week number')
    
    # Export command
    subparsers.add_parser('export', help='Export progress as JSON')
    
    # Velocity command
    subparsers.add_parser('velocity', help='Show velocity metrics')
    
    args = parser.parse_args()
    
    tracker = ProjectTracker(args.path)
    
    if args.command == 'status':
        stats = tracker.get_progress_stats()
        print(f"📊 Project Progress:")
        print(f"Main Plan: {stats['main_plan']['completed_tasks']}/{stats['main_plan']['total_tasks']} ({stats['main_plan']['progress_percentage']}%)")
        print(f"Weekly: {stats['weekly_tracker']['completed_tasks']}/{stats['weekly_tracker']['total_tasks']} ({stats['weekly_tracker']['progress_percentage']}%)")
    
    elif args.command == 'update':
        completed = args.completed or not args.incomplete
        tracker.update_progress(args.task, completed)
    
    elif args.command == 'report':
        report = tracker.generate_status_report()
        print(report)
    
    elif args.command == 'weekly':
        tracker.create_weekly_tracker(args.week)
    
    elif args.command == 'export':
        export_path = tracker.export_progress_json()
        print(f"Progress exported to: {export_path}")
    
    elif args.command == 'velocity':
        velocity = tracker.get_velocity_report()
        print(f"📈 Velocity Metrics:")
        print(f"Days elapsed: {velocity['days_elapsed']}")
        print(f"Tasks per day: {velocity['tasks_per_day']}")
        print(f"Estimated completion: {velocity['estimated_completion']}")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()