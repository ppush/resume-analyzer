# Tests

This directory contains all test files for the resume analyzer project.

## Structure

```
tests/
├── unit/                           # Unit tests
│   ├── test_file_loader.py        # File loading tests
│   ├── test_llm_client.py         # LLM client tests
│   ├── test_main.py               # Main application tests
│   ├── test_parsing_prompts.py    # Parsing prompt tests
│   ├── test_project_prompts.py    # Project prompt tests
│   ├── test_prompt_base.py        # Base prompt tests
│   ├── test_resume_block_parser.py # Block parser tests
│   ├── test_resume_block_processor.py # Block processor tests
│   ├── test_resume_parser.py      # Resume parser tests
│   ├── test_resume_result_aggregator.py # Result aggregator tests
│   ├── test_skill_merger.py       # Skill merger tests
│   ├── test_skill_prompts.py      # Skill prompt tests
│   ├── test_language_prompts.py   # Language prompt tests
│   ├── test_experience_calculator.py # Experience calculator tests
│   ├── test_experience_analyzer.py # Experience analyzer tests
│   ├── test_block_processor.py    # Block processor tests
│   └── test_block_processor_new.py # New block processor tests
├── run_all_tests.py               # Test runner
└── README.md                      # This file
```

## Running Tests

### Run All Tests
```bash
python tests/run_all_tests.py
```

### Run Specific Test File
```bash
python -m pytest tests/unit/test_file_loader.py
```

### Run Tests with Coverage
```bash
python -m pytest tests/unit/ --cov=core --cov-report=html
```

## Test Categories

- **File Processing**: `test_file_loader.py` - Tests for DOCX/PDF file reading
- **LLM Integration**: `test_llm_client.py` - Tests for LLM client functionality
- **API Endpoints**: `test_main.py` - Tests for FastAPI endpoints
- **Prompts**: `test_*_prompts.py` - Tests for various prompt classes
- **Parsing**: `test_resume_*_parser.py` - Tests for resume parsing logic
- **Processing**: `test_block_processor*.py` - Tests for block processing
- **Aggregation**: `test_resume_result_aggregator.py` - Tests for result aggregation
- **Experience**: `test_experience_*.py` - Tests for experience calculation
- **Skills**: `test_skill_*.py` - Tests for skill processing

## Test Data

Test data files are located in `tests/resources/` directory:
- Sample DOCX resumes
- Sample PDF resumes
- Test configuration files

## Notes

- All tests use the `unittest` framework
- Tests are designed to run without external dependencies (LLM mocking)
- Async tests are properly handled with proper mocking
- Test coverage includes both success and error scenarios
