# Integration Tests

## Overview
Integration tests for checking the complete resume analysis process.

## Files

### `test_full_pipeline.py`
Main integration test that can be used as:
1. **Unit test** - for checking component integration
2. **Command line tool** - for analyzing real resumes

## Usage

### Running as Unit test
```bash
# Run all integration tests
python -m unittest tests.integration.test_full_pipeline -v

# Run specific test
python -m unittest tests.integration.test_full_pipeline.TestFullPipeline.test_full_pipeline_integration -v
```

### Running as command line tool

#### Basic usage
```bash
python tests/integration/test_full_pipeline.py input_resume.txt output_result.json
```

#### With --test flag to run unit tests
```bash
python tests/integration/test_full_pipeline.py --test
```

## Arguments

- `input_file`: Path to resume file for analysis
- `output_file`: Path to file for writing analysis result
- `--test`: Run unit tests instead of resume analysis

## Example

```bash
# Resume analysis
python tests/integration/test_full_pipeline.py resume.txt result.json

# Run tests
python tests/integration/test_full_pipeline.py --test
```

## Features

✅ **Complete resume analysis process**
- Block splitting
- Block processing through LLM
- Results aggregation
- Work experience calculation

✅ **Usage flexibility**
- Can be run as test
- Can be used as tool
- Support for various file formats

✅ **Detailed logging**
- Step-by-step process output
- Information about each stage
- Results summary

✅ **Error handling**
- File existence checking
- Input data validation
- Detailed error messages

## Output Format

Result is saved in JSON format with the following structure:

```json
{
  "summary": "...",
  "skills": [...],
  "projects": [...],
  "education": [...],
  "languages": [...],
  "experience": "..."
}
```

## Requirements

- Python 3.7+
- All dependencies from main project
- Access to LLM service (for real analysis)
- File read/write permissions
