# 📝 Changelog

## [Unreleased] - 2025-09-04

### 🚀 Major Refactoring
- **Simplified Architecture** - Removed all wrapper classes
- **Unified Testing** - Standardized on unittest (built into Python)
- **Cleaned Dependencies** - Removed unused tools (pytest, bandit, pre-commit)
- **Updated CI/CD** - Synchronized with local development setup

### 🗑️ Removed
- `core/resume_block_parser.py` - Wrapper class
- `core/resume_block_processor.py` - Wrapper class
- `core/experience/__init__.py` - Unnecessary re-export
- `core/aggregator.py` - Old aggregator
- `core/recommender.py` - Old recommender
- All duplicate test files
- Outdated documentation files
- Temporary analysis scripts
- `__pycache__` directories

### 🔧 Updated
- **Import Structure** - Direct imports from core and services
- **CI/CD Pipeline** - Now uses unittest instead of pytest
- **Makefile** - Simplified commands
- **requirements-dev.txt** - Removed unused dependencies
- **pyproject.toml** - Simplified mypy configuration

### 📚 Documentation
- **README.md** - Updated architecture and commands
- **DEVELOPMENT.md** - New comprehensive development guide
- **PROJECT_INFO.md** - New project overview
- **CHANGELOG.md** - This file

### 🧪 Testing
- **145 tests passing** - All functionality preserved
- **unittest framework** - Standard Python testing
- **Consolidated tests** - Removed duplicates
- **Base test classes** - Shared test functionality

## [Previous Versions]

### Key Features Implemented
- LLM-based resume parsing
- DOCX and PDF support
- Parallel block processing
- Skills extraction and scoring
- Experience calculation
- Role identification from projects
- Comprehensive error handling
- Async/await support

### Architecture Principles
- SOLID principles
- Clean separation of concerns
- Mockable dependencies
- Comprehensive testing
- Clear documentation
