# Testing Guide - YouTube to MP3 Converter

## 🧪 How to Run Tests

### Prerequisites
Make sure you have the project dependencies installed:

```bash
# Install all dependencies (including testing tools)
pip install -r requirements.txt

# Or install the package in development mode
pip install -e .
```

### Basic Test Execution

#### Run All Tests
```bash
# From project root directory
python -m pytest

# With verbose output
python -m pytest -v

# Run tests in specific directory
python -m pytest tests/ -v
```

#### Run Specific Test Files
```bash
# Test only configuration functionality
python -m pytest tests/test_config.py -v

# Test only download functionality  
python -m pytest tests/test_downloader.py -v

# Test only CLI functionality
python -m pytest tests/test_cli.py -v
```

#### Run Specific Test Methods
```bash
# Run a specific test method
python -m pytest tests/test_config.py::TestConfigManager::test_get_default_config -v

# Run all tests in a specific class
python -m pytest tests/test_cli.py::TestCLI -v
```

### Advanced Test Options

#### Test Coverage
```bash
# Run tests with coverage report
python -m pytest --cov=src --cov-report=term-missing

# Generate HTML coverage report
python -m pytest --cov=src --cov-report=html

# View HTML report (opens in browser)
open htmlcov/index.html
```

#### Test Output Control
```bash
# Show print statements during tests
python -m pytest -s

# Stop on first failure
python -m pytest -x

# Show local variables in tracebacks
python -m pytest -l

# Run tests in parallel (if pytest-xdist installed)
python -m pytest -n auto
```

#### Filtering Tests
```bash
# Run tests matching a pattern
python -m pytest -k "config" -v

# Run tests with specific markers (if defined)
python -m pytest -m "slow" -v

# Skip tests matching a pattern
python -m pytest -k "not slow" -v
```

## 📊 Test Structure Overview

### Test Files and Coverage

| Test File | Purpose | Test Count | Coverage |
|-----------|---------|------------|----------|
| `test_config.py` | ConfigManager functionality | 10 tests | Configuration management, JSON handling, defaults |
| `test_downloader.py` | YouTubeDownloader functionality | 12 tests | URL validation, video info, download process |
| `test_cli.py` | CLI interface functionality | 14 tests | Argument parsing, interactive mode, config commands |
| **Total** | **Complete application coverage** | **36 tests** | **All major functionality** |

### Test Categories

#### **Configuration Tests (`test_config.py`)**
- ✅ Default configuration generation
- ✅ Configuration file loading and saving
- ✅ Setting updates and persistence
- ✅ Error handling (invalid JSON, IO errors)
- ✅ Path expansion and validation

#### **Download Tests (`test_downloader.py`)**
- ✅ URL validation (YouTube.com, youtu.be, invalid URLs)
- ✅ Video information extraction
- ✅ Download process with various scenarios
- ✅ Directory creation and error handling
- ✅ yt-dlp integration and configuration

#### **CLI Tests (`test_cli.py`)**
- ✅ Command-line argument parsing
- ✅ Interactive mode functionality
- ✅ Configuration command handling
- ✅ Error scenarios and user input validation

## 🔧 Test Configuration

### pytest Configuration (`pyproject.toml`)
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --tb=short"
```

### Coverage Configuration
```toml
[tool.coverage.run]
source = ["src"]
omit = ["tests/*", "setup.py"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "if self.debug:",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
]
```

## 🎯 Testing Best Practices

### Mocking Strategy
The tests use comprehensive mocking to isolate units and avoid external dependencies:

- **File System Operations**: Mocked using `tempfile` and `unittest.mock`
- **yt-dlp Integration**: Mocked to avoid actual YouTube API calls
- **User Input**: Mocked using `patch('builtins.input')`
- **Print Statements**: Mocked to verify output messages

### Test Data Management
- **Temporary Files**: Tests create and clean up temporary config files
- **Mock Objects**: Realistic mock data for video information and responses
- **Edge Cases**: Tests cover error conditions and invalid inputs

### Assertion Patterns
```python
# Configuration assertions
self.assertEqual(config["audio_quality"], "192")
self.assertIn("download_path", config)

# Mock call verification
mock_function.assert_called_once_with(expected_args)
mock_function.assert_not_called()

# Exception handling
with self.assertRaises(ExpectedException):
    function_that_should_fail()
```

## 🚀 Continuous Integration

### GitHub Actions Example
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.7, 3.8, 3.9, 3.10, 3.11]
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: ${{ matrix.python-version }}
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    - name: Run tests
      run: |
        python -m pytest --cov=src --cov-report=xml
    - name: Upload coverage
      uses: codecov/codecov-action@v1
```

## 🐛 Debugging Tests

### Common Issues and Solutions

#### **Import Errors**
```bash
# Problem: ModuleNotFoundError
# Solution: Install dependencies
pip install -r requirements.txt

# Problem: Can't find src modules
# Solution: Run from project root
cd /path/to/yt2mp3
python -m pytest
```

#### **Test Failures**
```bash
# Get detailed failure information
python -m pytest --tb=long

# Drop into debugger on failure
python -m pytest --pdb

# Show local variables in failures
python -m pytest -l
```

#### **Mock Issues**
```python
# Reset mocks between tests
def setUp(self):
    self.mock_object.reset_mock()

# Verify mock calls
print(mock_object.call_args_list)
```

## 📈 Test Metrics

### Current Test Results
```
============================= test session starts ==============================
platform darwin -- Python 3.10.16, pytest-8.4.1, pluggy-1.6.0
rootdir: /Users/albert/Desktop/web/yt2mp3
configfile: pyproject.toml
plugins: cov-6.2.1
collecting ... collected 36 items

tests/test_cli.py::TestCLI::test_cli_initialization PASSED               [  2%]
tests/test_cli.py::TestCLI::test_handle_config_commands_no_config_commands PASSED [  5%]
[... all tests passing ...]
============================== 36 passed in 0.14s ==============================
```

### Coverage Goals
- **Target**: 90%+ code coverage
- **Current**: All major functionality covered
- **Focus Areas**: Error handling, edge cases, user interaction flows

## 🔄 Adding New Tests

### Test File Template
```python
import unittest
from unittest.mock import Mock, patch
from src.yt2mp3.your_module import YourClass

class TestYourClass(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.instance = YourClass()
    
    def tearDown(self):
        """Clean up after each test method."""
        pass
    
    def test_your_functionality(self):
        """Test description."""
        # Arrange
        expected_result = "expected"
        
        # Act
        result = self.instance.your_method()
        
        # Assert
        self.assertEqual(result, expected_result)

if __name__ == '__main__':
    unittest.main()
```

### Running New Tests
```bash
# Run your new test file
python -m pytest tests/test_your_new_file.py -v

# Add to the full test suite
python -m pytest tests/ -v
```

This comprehensive testing setup ensures the YouTube to MP3 converter is reliable, maintainable, and ready for production use.