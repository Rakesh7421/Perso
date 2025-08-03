#!/usr/bin/env python3
"""
Git Management Script for Coderex Workspace
Manages commits across individual project repositories and main Coderex repository
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Optional


class Colors:
    """ANSI color codes for terminal output"""
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'


class GitManager:
    """Git repository manager for workspace"""
    
    def __init__(self, workspace_root: Path = None):
        self.workspace_root = workspace_root or Path.cwd()
        self.repositories = {
            'main': {
                'path': self.workspace_root,
                'name': 'Coderex (Main)',
                'type': 'main'
            },
            'NewsX': {
                'path': self.workspace_root / 'NewsX',
                'name': 'NewsX (Python CLI)',
                'type': 'project'
            },
            'Perso': {
                'path': self.workspace_root / 'Perso',
                'name': 'Perso (Static)',
                'type': 'project'
            },
            'react-vode-view': {
                'path': self.workspace_root / 'react-vode-view',
                'name': 'React Vode View (React/Vite)',
                'type': 'project'
            },
            'tereact': {
                'path': self.workspace_root / 'tereact',
                'name': 'Tereact (Static React)',
                'type': 'project'
            }
        }
    
    def print_header(self, title: str):
        """Print a formatted header"""
        print(f"\n{Colors.BLUE}{'=' * 60}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}{title.center(60)}{Colors.END}")
        print(f"{Colors.BLUE}{'=' * 60}{Colors.END}\n")
    
    def print_success(self, message: str):
        """Print success message"""
        print(f"{Colors.GREEN}✅ {message}{Colors.END}")
    
    def print_warning(self, message: str):
        """Print warning message"""
        print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")
    
    def print_error(self, message: str):
        """Print error message"""
        print(f"{Colors.RED}❌ {message}{Colors.END}")
    
    def run_git_command(self, repo_path: Path, command: List[str]) -> tuple:
        """Run git command in specified repository"""
        try:
            result = subprocess.run(
                ['git'] + command,
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=False
            )
            return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
        except Exception as e:
            return False, "", str(e)
    
    def check_git_status(self, repo_key: str) -> Dict:
        """Check git status for a repository"""
        repo = self.repositories[repo_key]
        repo_path = repo['path']
        
        if not (repo_path / '.git').exists():
            return {
                'exists': False,
                'clean': False,
                'staged': [],
                'modified': [],
                'untracked': [],
                'branch': None
            }
        
        # Get current branch
        success, branch, _ = self.run_git_command(repo_path, ['branch', '--show-current'])
        current_branch = branch if success else 'unknown'
        
        # Get status
        success, status_output, _ = self.run_git_command(repo_path, ['status', '--porcelain'])
        
        if not success:
            return {
                'exists': True,
                'clean': False,
                'staged': [],
                'modified': [],
                'untracked': [],
                'branch': current_branch
            }
        
        staged = []
        modified = []
        untracked = []
        
        for line in status_output.split('\n'):
            if not line.strip():
                continue
            
            status_code = line[:2]
            filename = line[3:]
            
            if status_code[0] in ['A', 'M', 'D', 'R', 'C']:
                staged.append(filename)
            if status_code[1] in ['M', 'D']:
                modified.append(filename)
            if status_code == '??':
                untracked.append(filename)
        
        return {
            'exists': True,
            'clean': len(staged) == 0 and len(modified) == 0 and len(untracked) == 0,
            'staged': staged,
            'modified': modified,
            'untracked': untracked,
            'branch': current_branch
        }
    
    def show_status_all(self):
        """Show status for all repositories"""
        self.print_header("🔍 GIT STATUS - ALL REPOSITORIES")
        
        for repo_key, repo_info in self.repositories.items():
            print(f"{Colors.BOLD}{repo_info['name']}{Colors.END}")
            print(f"Path: {repo_info['path']}")
            
            status = self.check_git_status(repo_key)
            
            if not status['exists']:
                self.print_warning("No Git repository found")
            else:
                print(f"Branch: {Colors.BLUE}{status['branch']}{Colors.END}")
                
                if status['clean']:
                    self.print_success("Working directory clean")
                else:
                    if status['staged']:
                        print(f"{Colors.GREEN}Staged files:{Colors.END}")
                        for file in status['staged']:
                            print(f"  + {file}")
                    
                    if status['modified']:
                        print(f"{Colors.YELLOW}Modified files:{Colors.END}")
                        for file in status['modified']:
                            print(f"  M {file}")
                    
                    if status['untracked']:
                        print(f"{Colors.RED}Untracked files:{Colors.END}")
                        for file in status['untracked']:
                            print(f"  ? {file}")
            
            print()
    
    def add_and_commit_repo(self, repo_key: str, message: str, add_all: bool = True):
        """Add and commit changes in a specific repository"""
        repo = self.repositories[repo_key]
        repo_path = repo['path']
        
        if not (repo_path / '.git').exists():
            self.print_error(f"No Git repository found in {repo['name']}")
            return False
        
        # Add files
        if add_all:
            success, _, error = self.run_git_command(repo_path, ['add', '.'])
            if not success:
                self.print_error(f"Failed to add files in {repo['name']}: {error}")
                return False
        
        # Commit
        success, output, error = self.run_git_command(repo_path, ['commit', '-m', message])
        if success:
            self.print_success(f"Committed changes in {repo['name']}")
            return True
        elif 'nothing to commit' in error:
            self.print_warning(f"No changes to commit in {repo['name']}")
            return True
        else:
            self.print_error(f"Failed to commit in {repo['name']}: {error}")
            return False
    
    def commit_all_projects(self, message: str):
        """Commit changes in all project repositories"""
        self.print_header("📝 COMMITTING ALL PROJECT REPOSITORIES")
        
        success_count = 0
        total_count = 0
        
        for repo_key, repo_info in self.repositories.items():
            if repo_info['type'] == 'project':
                total_count += 1
                print(f"\n{Colors.BOLD}Committing {repo_info['name']}...{Colors.END}")
                if self.add_and_commit_repo(repo_key, message):
                    success_count += 1
        
        print(f"\n{Colors.BOLD}Project commits: {success_count}/{total_count} successful{Colors.END}")
    
    def commit_main_repo(self, message: str):
        """Commit changes in main Coderex repository"""
        self.print_header("📝 COMMITTING MAIN CODEREX REPOSITORY")
        
        print(f"{Colors.BOLD}Committing Coderex (Main)...{Colors.END}")
        self.add_and_commit_repo('main', message)
    
    def commit_all(self, project_message: str, main_message: str = None):
        """Commit changes in all repositories"""
        # Commit individual projects first
        self.commit_all_projects(project_message)
        
        # Then commit main repository
        main_msg = main_message or f"Update shared environment - {project_message}"
        self.commit_main_repo(main_msg)
    
    def initialize_missing_repos(self):
        """Initialize Git repositories for projects that don't have them"""
        self.print_header("🚀 INITIALIZING MISSING GIT REPOSITORIES")
        
        for repo_key, repo_info in self.repositories.items():
            repo_path = repo_info['path']
            
            if not repo_path.exists():
                self.print_warning(f"Directory doesn't exist: {repo_info['name']}")
                continue
            
            if not (repo_path / '.git').exists():
                print(f"Initializing Git repository for {repo_info['name']}...")
                success, output, error = self.run_git_command(repo_path.parent, ['init', repo_path.name])
                
                if success:
                    self.print_success(f"Initialized Git repository for {repo_info['name']}")
                else:
                    self.print_error(f"Failed to initialize Git for {repo_info['name']}: {error}")
            else:
                self.print_success(f"Git repository already exists for {repo_info['name']}")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Git Management for Coderex Workspace")
    parser.add_argument('--status', action='store_true', help='Show status of all repositories')
    parser.add_argument('--init', action='store_true', help='Initialize missing Git repositories')
    parser.add_argument('--commit-projects', help='Commit all project repositories with message')
    parser.add_argument('--commit-main', help='Commit main Coderex repository with message')
    parser.add_argument('--commit-all', help='Commit all repositories with message')
    parser.add_argument('--main-message', help='Custom message for main repository (used with --commit-all)')
    
    args = parser.parse_args()
    
    manager = GitManager()
    
    if args.status:
        manager.show_status_all()
    elif args.init:
        manager.initialize_missing_repos()
    elif args.commit_projects:
        manager.commit_all_projects(args.commit_projects)
    elif args.commit_main:
        manager.commit_main_repo(args.commit_main)
    elif args.commit_all:
        manager.commit_all(args.commit_all, args.main_message)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()