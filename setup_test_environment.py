#!/usr/bin/env python3
"""
Complete Test Environment Setup Script
Finalizes the shared test environment setup and validates everything works
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(command, description, check=True):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=check, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - SUCCESS")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()}")
        else:
            print(f"❌ {description} - FAILED")
            if result.stderr.strip():
                print(f"   Error: {result.stderr.strip()}")
        return result.returncode == 0
    except Exception as e:
        print(f"❌ {description} - ERROR: {e}")
        return False


def check_file_exists(filepath, description):
    """Check if a file exists"""
    if Path(filepath).exists():
        print(f"✅ {description} - EXISTS")
        return True
    else:
        print(f"❌ {description} - MISSING")
        return False


def main():
    """Main setup function"""
    print("🚀 FINALIZING SHARED TEST ENVIRONMENT SETUP")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("activate_shared.sh").exists():
        print("❌ Please run this script from the Coderex root directory")
        sys.exit(1)
    
    # Activate virtual environment and install remaining dependencies
    print("\n📦 INSTALLING DEVELOPMENT DEPENDENCIES")
    print("-" * 40)
    
    success = run_command(
        "bash -c 'source .venv/bin/activate && pip install -r requirements-dev.txt'",
        "Installing development dependencies"
    )
    
    if not success:
        print("⚠️  Development dependencies installation failed, continuing...")
    
    # Verify key files exist
    print("\n📁 VERIFYING FILE STRUCTURE")
    print("-" * 40)
    
    files_to_check = [
        (".venv/bin/activate", "Virtual environment"),
        ("requirements.txt", "Core requirements"),
        ("requirements-dev.txt", "Development requirements"),
        ("requirements-test.txt", "Testing requirements"),
        ("pytest.ini", "Pytest configuration"),
        ("activate_shared.sh", "Activation script"),
        ("test_runner.py", "Unified test runner"),
        ("TEST_SETUP_GUIDE.md", "Setup documentation"),
        ("NewsX/Newsfetch/tests/__init__.py", "NewsX test init"),
        ("NewsX/Newsfetch/tests/test_newsx.py", "NewsX sample tests"),
        ("NewsX/Newsfetch/tests/test_news_fetcher.py", "NewsX news_fetcher tests"),
        ("NewsX/Newsfetch/tests/test_utils.py", "NewsX utils tests"),
    ]
    
    all_files_exist = True
    for filepath, description in files_to_check:
        if not check_file_exists(filepath, description):
            all_files_exist = False
    
    # Test the unified test runner
    print("\n🧪 TESTING UNIFIED TEST RUNNER")
    print("-" * 40)
    
    run_command(
        "bash -c 'source .venv/bin/activate && python test_runner.py --list-projects'",
        "Listing available projects",
        check=False
    )
    
    # Run a quick test
    print("\n🔬 RUNNING SAMPLE TESTS")
    print("-" * 40)
    
    run_command(
        "bash -c 'source .venv/bin/activate && python -m pytest NewsX/Newsfetch/tests/test_newsx.py -v'",
        "Running sample tests",
        check=False
    )
    
    # Check Python and pip versions
    print("\n🐍 ENVIRONMENT INFORMATION")
    print("-" * 40)
    
    run_command(
        "bash -c 'source .venv/bin/activate && python --version'",
        "Python version",
        check=False
    )
    
    run_command(
        "bash -c 'source .venv/bin/activate && pip --version'",
        "Pip version",
        check=False
    )
    
    run_command(
        "bash -c 'source .venv/bin/activate && pip list | grep pytest'",
        "Pytest installation",
        check=False
    )
    
    # Create a summary report
    print("\n📊 SETUP SUMMARY")
    print("=" * 50)
    
    if all_files_exist:
        print("✅ All required files are present")
    else:
        print("⚠️  Some files are missing - check the output above")
    
    print("\n🎯 NEXT STEPS:")
    print("1. Activate the environment: source activate_shared.sh")
    print("2. Install dependencies: install-deps")
    print("3. Run tests: run-tests")
    print("4. Read the guide: cat TEST_SETUP_GUIDE.md")
    
    print("\n🎉 SHARED TEST ENVIRONMENT SETUP COMPLETE!")
    print("\nFor detailed usage instructions, see TEST_SETUP_GUIDE.md")


if __name__ == "__main__":
    main()