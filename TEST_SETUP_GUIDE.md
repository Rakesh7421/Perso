# 🧪 Shared Test Environment Setup Guide

## 📋 Overview

This guide explains the shared virtual environment setup for all projects in the Coderex workspace. The setup provides a unified testing environment while keeping project files in their respective directories.

## 🏗️ Architecture

```
/home/rakesh/Coderex/
├── .venv/                    # Shared virtual environment
├── requirements.txt          # Core dependencies
├── requirements-dev.txt      # Development tools
├── requirements-test.txt     # Testing frameworks
├── pytest.ini              # Pytest configuration
├── activate_shared.sh       # Environment activation script
├── test_runner.py          # Unified test runner
├── TEST_SETUP_GUIDE.md     # This guide
├── NewsX/                  # Python CLI project
├── react-vode-view/        # React/Vite project
├── Perso/                  # Static HTML project
└── tereact/                # Vanilla React project
```

## 🚀 Quick Start

### 1. Activate the Shared Environment
```bash
# Navigate to Coderex directory
cd /home/rakesh/Coderex

# Activate shared environment
source activate_shared.sh
```

### 2. Install Dependencies
```bash
# Install core dependencies
install-deps

# Install development tools
install-dev

# Install testing frameworks
install-test
```

### 3. Create Test Directories
```bash
# Create test directories for all projects
python test_runner.py --create-dirs
```

### 4. Run Tests
```bash
# Run all tests
run-tests

# Or use the test runner directly
python test_runner.py

# Run tests for specific projects
python test_runner.py --projects NewsX react-vode-view
```

## 📦 Dependencies

### Core Dependencies (`requirements.txt`)
- `requests>=2.32.4` - HTTP library for NewsX project

### Development Dependencies (`requirements-dev.txt`)
- `pytest>=7.0.0` - Testing framework
- `pytest-cov>=4.0.0` - Coverage reporting
- `black>=23.0.0` - Code formatting
- `flake8>=6.0.0` - Code linting
- `mypy>=1.0.0` - Type checking
- `pre-commit>=3.0.0` - Git hooks
- `sphinx>=5.0.0` - Documentation generation

### Testing Dependencies (`requirements-test.txt`)
- `pytest` and plugins for comprehensive testing
- `factory-boy` and `faker` for test data generation
- `responses` and `httpx` for API testing
- `pytest-benchmark` for performance testing

## 🧪 Testing Strategy

### Python Projects (NewsX)
- **Framework**: pytest with coverage reporting
- **Location**: `NewsX/Newsfetch/tests/`
- **Configuration**: Shared `pytest.ini`
- **Commands**: 
  ```bash
  pytest NewsX/Newsfetch/tests/ -v
  pytest --cov=NewsX/Newsfetch
  ```

### React Projects (react-vode-view)
- **Framework**: npm test (project-specific)
- **Location**: `react-vode-view/tests/`
- **Commands**:
  ```bash
  cd react-vode-view
  npm test
  ```

### Static Projects (Perso, tereact)
- **Validation**: Basic file existence checks
- **Location**: `{project}/tests/` (optional)
- **Commands**: Handled by unified test runner

## 🔧 Available Commands

After activating the shared environment, these aliases are available:

| Command | Description |
|---------|-------------|
| `install-deps` | Install core dependencies |
| `install-dev` | Install development dependencies |
| `install-test` | Install testing dependencies |
| `run-tests` | Run all tests using unified runner |
| `run-linting` | Run code linting and formatting checks |
| `deactivate` | Exit virtual environment |

## 📊 Test Runner Features

The unified test runner (`test_runner.py`) provides:

### Commands
```bash
# Run all tests
python test_runner.py

# Run specific projects
python test_runner.py --projects NewsX react-vode-view

# List available projects
python test_runner.py --list-projects

# Create test directories
python test_runner.py --create-dirs
```

### Features
- ✅ **Multi-language support**: Python, Node.js, static files
- ✅ **Colored output**: Clear visual feedback
- ✅ **Project detection**: Automatic test discovery
- ✅ **Summary reporting**: Overall pass/fail status
- ✅ **Directory creation**: Auto-setup test directories

## 🔄 Dependency Management

### Adding New Dependencies

#### For All Projects
```bash
# Add to requirements.txt
echo "new-package>=1.0.0" >> requirements.txt
install-deps
```

#### For Development Only
```bash
# Add to requirements-dev.txt
echo "dev-package>=1.0.0" >> requirements-dev.txt
install-dev
```

#### For Testing Only
```bash
# Add to requirements-test.txt
echo "test-package>=1.0.0" >> requirements-test.txt
install-test
```

### Handling Conflicts

When dependency conflicts arise:

1. **Document the conflict** in `DEPENDENCY_CONFLICTS.md`
2. **Create project-specific venv** for conflicting project:
   ```bash
   cd NewsX/Newsfetch
   python -m venv .venv-newsX
   source .venv-newsX/bin/activate
   ```
3. **Update activation scripts** to handle multiple environments
4. **Keep shared venv** for non-conflicting projects

## 🎯 Project-Specific Setup

### NewsX (Python CLI)
```bash
# Navigate to project
cd NewsX/Newsfetch

# Run project-specific tests
pytest tests/ -v

# Run with coverage
pytest --cov=. tests/

# Set up API key for testing
export NEWSAPI_KEY="your-test-api-key"
```

### react-vode-view (React/Vite)
```bash
# Navigate to project
cd react-vode-view

# Install Node dependencies
npm install

# Run tests (if configured)
npm test

# Run development server
npm run dev
```

### Perso & tereact (Static)
```bash
# Basic validation
python test_runner.py --projects Perso tereact

# Manual testing: open in browser
# Perso: file:///home/rakesh/Coderex/Perso/index.html
# tereact: file:///home/rakesh/Coderex/tereact/index.html
```

## 🔍 Monitoring and Maintenance

### Regular Tasks
```bash
# Update all dependencies
pip list --outdated
pip install --upgrade -r requirements.txt

# Clean up cache
pip cache purge

# Check for security issues
pip audit

# Update Node dependencies (per project)
cd react-vode-view && npm audit && npm update
```

### Health Checks
```bash
# Verify environment
python --version
pip --version
which python

# Test all projects
python test_runner.py

# Check linting
run-linting
```

## 🚨 Troubleshooting

### Common Issues

#### Virtual Environment Not Activating
```bash
# Recreate environment
rm -rf .venv
python3 -m venv .venv --without-pip
source activate_shared.sh
```

#### Pip Installation Issues
```bash
# Manual pip installation
curl https://bootstrap.pypa.io/get-pip.py | python
pip install --upgrade pip
```

#### Test Discovery Issues
```bash
# Verify pytest configuration
pytest --collect-only

# Check test directories
python test_runner.py --list-projects
```

#### Permission Issues
```bash
# Fix script permissions
chmod +x activate_shared.sh
chmod +x test_runner.py
```

## 📈 Future Enhancements

### Planned Features
- [ ] **CI/CD Integration**: GitHub Actions workflow
- [ ] **Docker Support**: Containerized testing environment
- [ ] **Performance Monitoring**: Test execution time tracking
- [ ] **Automated Reporting**: HTML test reports with history
- [ ] **Pre-commit Hooks**: Automatic linting and testing

### Scalability Considerations
- **Multiple Python Versions**: Use `tox` for multi-version testing
- **Microservices**: Separate venvs for conflicting services
- **Database Testing**: Add test database setup
- **Integration Testing**: Cross-project integration tests

## 📞 Support

For issues or questions:
1. Check this guide first
2. Review project-specific documentation
3. Check the unified test runner help: `python test_runner.py --help`
4. Examine log files in project directories

---

**Happy Testing! 🎉**