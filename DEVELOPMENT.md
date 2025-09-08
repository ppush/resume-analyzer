# 🚀 Development Guide

## 📋 Quick Setup

### 1. Environment Setup
```bash
# Clone repository
git clone <repository-url>
cd resume-analyzer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install development dependencies
pip install -r requirements-dev.txt
```

### 2. Verify Setup
```bash
# Run tests to ensure everything works
python tests/run_all_tests.py

# Check code formatting
black . --check
isort . --check-only
```

## 🔧 Development Workflow

### Before Starting Work
```bash
# Ensure tests pass
python tests/run_all_tests.py

# Check code quality
flake8 .
mypy core/ services/
```

### During Development
```bash
# Format code automatically
black .
isort .

# Run specific tests
python -m unittest tests.unit.test_experience_calculator -v
```

### Before Committing
```bash
# Full quality check
black . --check
isort . --check-only
flake8 .
mypy core/ services/
python tests/run_all_tests.py
```

## 🧪 Testing

### Test Structure
- **`tests/unit/`** - Unit tests for individual components
- **`tests/integration/`** - Integration tests for full pipeline
- **`tests/run_all_tests.py`** - Main test runner

### Running Tests
```bash
# All tests
python tests/run_all_tests.py

# Specific test file
python -m unittest tests.unit.test_experience_calculator -v

# Specific test method
python -m unittest tests.unit.test_experience_calculator.TestExperienceCalculator.test_init -v
```

### Test Conventions
- Use `unittest.TestCase` as base class
- Test methods start with `test_`
- Use descriptive test names
- Mock external dependencies (LLM, file system)

## 📁 Project Structure

```
resume-analyzer/
├── core/                    # Core business logic
│   ├── __init__.py         # Module exports
│   ├── resume_parser.py    # Resume parsing
│   ├── block_processor.py  # Block processing
│   ├── experience_calculator.py  # Experience calculation
│   ├── aggregation/        # Result aggregation
│   │   ├── __init__.py
│   │   ├── resume_result_aggregator.py
│   │   ├── skill_merger.py
│   │   └── experience_analyzer.py
│   └── prompts/           # LLM prompts
│       ├── __init__.py
│       ├── prompt_base.py
│       ├── parsing_prompts.py
│       ├── project_prompts.py
│       ├── skill_prompts.py
│       └── language_prompts.py
├── services/               # External services
│   ├── __init__.py
│   ├── llm_client.py      # LLM integration
│   └── file_loader.py     # File processing
├── tests/                  # Test files
│   ├── run_all_tests.py   # Main test runner
│   ├── unit/              # Unit tests
│   └── integration/       # Integration tests
├── main.py                 # FastAPI application
├── run.py                  # Service runner
└── requirements.txt        # Dependencies
```

## 🎯 Key Principles

### 1. SOLID Principles
- **Single Responsibility** - Each class has one reason to change
- **Open/Closed** - Open for extension, closed for modification
- **Liskov Substitution** - Subtypes are substitutable
- **Interface Segregation** - Small, focused interfaces
- **Dependency Inversion** - Depend on abstractions, not concretions

### 2. Code Quality
- **Readability** - Code should be self-documenting
- **Consistency** - Follow established patterns
- **Testing** - All new code must have tests
- **Documentation** - Clear docstrings for public methods

### 3. Architecture
- **No Wrappers** - Direct usage of core components
- **Clear Dependencies** - Explicit import statements
- **Separation of Concerns** - Business logic separate from infrastructure
- **Async Support** - Use async/await for I/O operations

## 🚨 Common Issues

### Import Errors
```bash
# If you get import errors, ensure you're in the right directory
cd resume-analyzer
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Test Failures
```bash
# Clean up temporary files
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} +

# Re-run tests
python tests/run_all_tests.py
```

### Code Formatting Issues
```bash
# Auto-format code
black .
isort .

# Check formatting
black . --check
isort . --check-only
```

## 📚 Additional Resources

- **Python unittest**: https://docs.python.org/3/library/unittest.html
- **Black formatting**: https://black.readthedocs.io/
- **isort**: https://pycqa.github.io/isort/
- **flake8**: https://flake8.pycqa.org/
- **mypy**: https://mypy.readthedocs.io/

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch
3. **Make** your changes
4. **Test** thoroughly
5. **Commit** with clear messages
6. **Push** to your branch
7. **Create** a pull request

### Commit Message Format
```
type(scope): description

- type: feat, fix, docs, style, refactor, test, chore
- scope: component or module affected
- description: clear, concise description
```

Example:
```
feat(experience): add duration validation

- Add input validation for duration fields
- Improve error handling for invalid formats
- Add unit tests for validation logic
```

## 🧪 Testing Commands

### Unittest (Traditional)
```bash
# Run all tests
python tests/run_all_tests.py

# Run specific test
python -m unittest tests.unit.test_experience_calculator -v
```

### Pytest (Recommended for Async)
```bash
# Run all tests
pytest tests/ -v

# Run async tests specifically
pytest tests/ -v --asyncio-mode=auto

# Run specific test file
pytest tests/unit/test_file_loader.py -v

# Run with coverage
pytest tests/ -v --cov=core --cov=services --cov-report=term
```

### Why Pytest for Async Tests?
- **No "coroutine never awaited" warnings** - pytest-asyncio properly handles async test methods
- **Better async support** - Built-in fixtures and markers for async testing
- **Cleaner output** - Less noise from unittest warnings
- **Modern approach** - Industry standard for Python testing
