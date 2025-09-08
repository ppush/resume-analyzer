# 🧪 Testing Guide

## 📋 Overview

This project supports two testing approaches:
- **Unittest** (traditional) - for simple tests
- **Pytest** (recommended) - for async tests and modern testing

## 🚀 Quick Start

### Install Dependencies
```bash
pip install -r requirements-dev.txt
```

### Run Tests
```bash
# All tests (unittest)
python tests/run_all_tests.py

# All tests (pytest)
pytest tests/ -v

# Async tests only (pytest)
pytest tests/ -v --asyncio-mode=auto
```

## 🔧 Testing Approaches

### 1. Unittest (Traditional)
```bash
# Run all tests
python tests/run_all_tests.py

# Run specific test file
python -m unittest tests.unit.test_experience_calculator -v

# Run specific test method
python -m unittest tests.unit.test_experience_calculator.TestExperienceCalculator.test_init -v
```

**Pros:**
- Built into Python
- Simple and familiar
- Good for basic tests

**Cons:**
- Async tests show "coroutine never awaited" warnings
- Less modern features
- Limited async support

### 2. Pytest (Recommended)
```bash
# Run all tests
pytest tests/ -v

# Run async tests specifically
pytest tests/ -v --asyncio-mode=auto

# Run specific test file
pytest tests/unit/test_file_loader.py -v

# Run with coverage
pytest tests/ -v --cov=core --cov=services --cov-report=term

# Run specific test method
pytest tests/unit/test_file_loader.py::TestFileLoader::test_read_resume_as_html_chunks_docx -v
```

**Pros:**
- No "coroutine never awaited" warnings
- Excellent async support
- Modern testing features
- Better output and reporting
- Industry standard

**Cons:**
- Requires additional installation
- Different syntax from unittest

## 🎯 Async Testing

### Problem
Unittest shows warnings like:
```
RuntimeWarning: coroutine 'TestFileLoader.test_read_resume_as_html_chunks_docx' was never awaited
```

### Solution
Use pytest with pytest-asyncio:

```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    result = await some_async_function()
    assert result == expected_value
```

### Configuration
The project includes:
- `pytest.ini` - pytest configuration
- `conftest.py` - pytest setup and fixtures
- `pytest-asyncio` - async testing support

## 🛠️ Test Commands

### Makefile Commands
```bash
make test          # Run unittest tests
make test-pytest   # Run pytest tests
make test-async    # Run async tests with pytest
make test-cov      # Run tests with coverage
```

### Individual Commands
```bash
# Unittest
python tests/run_all_tests.py
python -m unittest tests.unit.test_experience_calculator -v

# Pytest
pytest tests/ -v
pytest tests/ -v --asyncio-mode=auto
pytest tests/unit/test_file_loader.py -v

# Coverage
pytest tests/ -v --cov=core --cov=services --cov-report=html
```

## 📁 Test Structure

```
tests/
├── run_all_tests.py          # Unittest runner
├── unit/                     # Unit tests
│   ├── test_file_loader.py
│   ├── test_experience_calculator.py
│   └── ...
├── integration/              # Integration tests
│   └── test_full_pipeline.py
└── conftest.py              # Pytest configuration
```

## 🎨 Writing Tests

### Unittest Style
```python
import unittest
from unittest.mock import patch, Mock

class TestExample(unittest.TestCase):
    def test_sync_function(self):
        result = some_function()
        self.assertEqual(result, expected_value)
    
    @patch('module.function')
    async def test_async_function(self, mock_func):
        mock_func.return_value = "mocked"
        result = await async_function()
        self.assertEqual(result, "mocked")
```

### Pytest Style
```python
import pytest
from unittest.mock import patch, Mock

def test_sync_function():
    result = some_function()
    assert result == expected_value

@pytest.mark.asyncio
async def test_async_function():
    with patch('module.function') as mock_func:
        mock_func.return_value = "mocked"
        result = await async_function()
        assert result == "mocked"
```

## 🚨 Common Issues

### Import Errors
```bash
# Ensure you're in the project root
cd resume-analyzer

# Set Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Async Test Warnings
```bash
# Use pytest instead of unittest for async tests
pytest tests/ -v --asyncio-mode=auto
```

### Test Discovery Issues
```bash
# Clean up cache
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} +

# Re-run tests
pytest tests/ -v
```

## 📊 Coverage

### Generate Coverage Report
```bash
# HTML report
pytest tests/ -v --cov=core --cov=services --cov-report=html

# Terminal report
pytest tests/ -v --cov=core --cov=services --cov-report=term

# XML report (for CI/CD)
pytest tests/ -v --cov=core --cov=services --cov-report=xml
```

### Coverage Configuration
Coverage is configured in `pytest.ini` and CI/CD pipeline.

## 🔄 CI/CD Integration

The project includes GitHub Actions that run:
1. **Unittest tests** - `python tests/run_all_tests.py`
2. **Pytest async tests** - `pytest tests/ -v --asyncio-mode=auto`

## 📚 Resources

- **Pytest**: https://docs.pytest.org/
- **Pytest-asyncio**: https://pytest-asyncio.readthedocs.io/
- **Python unittest**: https://docs.python.org/3/library/unittest.html
- **Coverage.py**: https://coverage.readthedocs.io/

