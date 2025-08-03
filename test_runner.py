#!/usr/bin/env python3
"""
Unified Test Runner for Coderex Projects
Runs tests for all projects in the workspace
"""

import os
import sys
import subprocess
import argparse
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


class TestRunner:
    """Unified test runner for all projects"""
    
    def __init__(self, workspace_root: Path = None):
        self.workspace_root = workspace_root or Path.cwd()
        self.projects = {
            'NewsX': {
                'path': self.workspace_root / 'NewsX' / 'Newsfetch',
                'type': 'python',
                'test_command': ['python', '-m', 'pytest', 'tests/', '-v'],
                'has_tests': True
            },
            'react-vode-view': {
                'path': self.workspace_root / 'react-vode-view',
                'type': 'node',
                'test_command': ['npm', 'test'],
                'has_tests': False  # Will check dynamically
            },
            'Perso': {
                'path': self.workspace_root / 'Perso',
                'type': 'static',
                'test_command': None,
                'has_tests': False
            },
            'tereact': {
                'path': self.workspace_root / 'tereact',
                'type': 'static',
                'test_command': None,
                'has_tests': False
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
    
    def check_project_tests(self, project_name: str, project_info: Dict) -> bool:
        """Check if a project has tests"""
        project_path = project_info['path']
        
        if not project_path.exists():
            return False
        
        # Check for common test directories/files
        test_patterns = [
            project_path / 'tests',
            project_path / 'test',
            project_path / '__tests__',
            project_path / 'spec'
        ]
        
        for pattern in test_patterns:
            if pattern.exists() and any(pattern.iterdir()):
                return True
        
        # Check for test files in root
        test_files = list(project_path.glob('*test*.py')) + list(project_path.glob('*test*.js'))
        return len(test_files) > 0
    
    def run_python_tests(self, project_name: str, project_info: Dict) -> bool:
        """Run Python tests using pytest"""
        project_path = project_info['path']
        
        if not self.check_project_tests(project_name, project_info):
            self.print_warning(f"No tests found for {project_name}")
            return True
        
        print(f"{Colors.BLUE}🐍 Running Python tests for {project_name}...{Colors.END}")
        
        try:
            # Change to project directory
            original_cwd = os.getcwd()
            os.chdir(project_path)
            
            # Run pytest
            result = subprocess.run(
                ['python', '-m', 'pytest', '-v', '--tb=short'],
                capture_output=False,
                text=True
            )
            
            os.chdir(original_cwd)
            
            if result.returncode == 0:
                self.print_success(f"Python tests passed for {project_name}")
                return True
            else:
                self.print_error(f"Python tests failed for {project_name}")
                return False
                
        except Exception as e:
            self.print_error(f"Error running Python tests for {project_name}: {e}")
            return False
    
    def run_node_tests(self, project_name: str, project_info: Dict) -> bool:
        """Run Node.js tests using npm"""
        project_path = project_info['path']
        
        if not (project_path / 'package.json').exists():
            self.print_warning(f"No package.json found for {project_name}")
            return True
        
        print(f"{Colors.BLUE}📦 Running Node.js tests for {project_name}...{Colors.END}")
        
        try:
            # Change to project directory
            original_cwd = os.getcwd()
            os.chdir(project_path)
            
            # Check if test script exists
            result = subprocess.run(
                ['npm', 'run', 'test'],
                capture_output=True,
                text=True
            )
            
            os.chdir(original_cwd)
            
            if result.returncode == 0:
                self.print_success(f"Node.js tests passed for {project_name}")
                return True
            else:
                if "Missing script" in result.stderr:
                    self.print_warning(f"No test script defined for {project_name}")
                    return True
                else:
                    self.print_error(f"Node.js tests failed for {project_name}")
                    print(result.stdout)
                    print(result.stderr)
                    return False
                    
        except Exception as e:
            self.print_error(f"Error running Node.js tests for {project_name}: {e}")
            return False
    
    def run_static_checks(self, project_name: str, project_info: Dict) -> bool:
        """Run basic checks for static projects"""
        project_path = project_info['path']
        
        if not project_path.exists():
            self.print_warning(f"Project directory not found: {project_name}")
            return True
        
        print(f"{Colors.BLUE}📄 Checking static project {project_name}...{Colors.END}")
        
        # Check for HTML files
        html_files = list(project_path.glob('*.html'))
        if html_files:
            self.print_success(f"Found {len(html_files)} HTML file(s) in {project_name}")
        else:
            self.print_warning(f"No HTML files found in {project_name}")
        
        return True
    
    def run_project_tests(self, project_name: str, project_info: Dict) -> bool:
        """Run tests for a specific project"""
        project_type = project_info['type']
        
        if project_type == 'python':
            return self.run_python_tests(project_name, project_info)
        elif project_type == 'node':
            return self.run_node_tests(project_name, project_info)
        elif project_type == 'static':
            return self.run_static_checks(project_name, project_info)
        else:
            self.print_warning(f"Unknown project type: {project_type}")
            return True
    
    def run_all_tests(self, projects: Optional[List[str]] = None) -> bool:
        """Run tests for all or specified projects"""
        self.print_header("🧪 UNIFIED TEST RUNNER")
        
        projects_to_test = projects or list(self.projects.keys())
        results = {}
        
        for project_name in projects_to_test:
            if project_name not in self.projects:
                self.print_error(f"Unknown project: {project_name}")
                continue
            
            print(f"\n{Colors.BOLD}Testing {project_name}...{Colors.END}")
            results[project_name] = self.run_project_tests(project_name, self.projects[project_name])
        
        # Print summary
        self.print_header("📊 TEST SUMMARY")
        
        passed = sum(1 for result in results.values() if result)
        total = len(results)
        
        for project_name, result in results.items():
            if result:
                self.print_success(f"{project_name}: PASSED")
            else:
                self.print_error(f"{project_name}: FAILED")
        
        print(f"\n{Colors.BOLD}Overall: {passed}/{total} projects passed{Colors.END}")
        
        return all(results.values())
    
    def create_test_directories(self):
        """Create test directories for projects that don't have them"""
        self.print_header("📁 CREATING TEST DIRECTORIES")
        
        for project_name, project_info in self.projects.items():
            project_path = project_info['path']
            
            if not project_path.exists():
                continue
            
            test_dir = project_path / 'tests'
            if not test_dir.exists():
                test_dir.mkdir(parents=True, exist_ok=True)
                self.print_success(f"Created test directory for {project_name}")
                
                # Create __init__.py for Python projects
                if project_info['type'] == 'python':
                    (test_dir / '__init__.py').touch()
                    
                    # Create a sample test file
                    sample_test = test_dir / f'test_{project_name.lower().replace("-", "_")}.py'
                    if not sample_test.exists():
                        sample_test.write_text(f'''"""
Sample test file for {project_name}
"""

import pytest


def test_sample():
    """Sample test that always passes"""
    assert True


def test_{project_name.lower().replace("-", "_")}_exists():
    """Test that the project exists"""
    import pathlib
    project_path = pathlib.Path(__file__).parent.parent
    assert project_path.exists()
''')
                        self.print_success(f"Created sample test file for {project_name}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Unified Test Runner for Coderex Projects")
    parser.add_argument(
        '--projects', '-p',
        nargs='+',
        help='Specific projects to test (default: all)'
    )
    parser.add_argument(
        '--create-dirs',
        action='store_true',
        help='Create test directories for projects'
    )
    parser.add_argument(
        '--list-projects',
        action='store_true',
        help='List all available projects'
    )
    
    args = parser.parse_args()
    
    runner = TestRunner()
    
    if args.list_projects:
        runner.print_header("📋 AVAILABLE PROJECTS")
        for project_name, project_info in runner.projects.items():
            print(f"  {Colors.BLUE}{project_name}{Colors.END} ({project_info['type']})")
        return
    
    if args.create_dirs:
        runner.create_test_directories()
        return
    
    success = runner.run_all_tests(args.projects)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()