# 📊 Project Information

## 🎯 Overview

**Resume Analyzer** is an AI-powered service that analyzes resumes using local LLM (LM Studio) to extract skills, experience, and other relevant information.

## 🏗️ Architecture

- **Simplified Design** - No wrapper classes, direct component usage
- **SOLID Principles** - Clean, maintainable code structure
- **Async Support** - Built for performance with async/await
- **LLM Integration** - Uses local LM Studio for privacy and control

## 🔧 Technology Stack

- **Python 3.8+** - Core language
- **FastAPI** - Web framework
- **unittest** - Testing framework (built into Python)
- **Black + isort** - Code formatting
- **flake8** - Linting
- **mypy** - Type checking
- **LM Studio** - Local LLM server

## 📁 Key Components

### Core Logic
- **ResumeParser** - Divides resumes into structured blocks
- **BlockProcessor** - Processes blocks through LLM
- **ExperienceCalculator** - Calculates work experience
- **SkillMerger** - Deduplicates and merges skills
- **ExperienceAnalyzer** - Analyzes and formats experience

### Services
- **LLMClient** - Integration with LM Studio
- **FileLoader** - DOCX/PDF text extraction

### Prompts
- **PromptBase** - Base class for all LLM prompts
- **Specialized prompts** for parsing, skills, projects, languages

## 🧪 Testing

- **145 unit tests** covering all components
- **unittest framework** - Standard Python testing
- **Mocking** for external dependencies
- **Integration tests** for full pipeline

## 🚀 Quick Commands

```bash
# Run service
python run.py

# Run tests
python tests/run_all_tests.py

# Format code
black .
isort .

# Check quality
flake8 .
mypy core/ services/
```

## 📈 Recent Improvements

- ✅ **Removed wrapper classes** - Simplified architecture
- ✅ **Unified testing** - Standardized on unittest
- ✅ **Cleaned dependencies** - Removed unused tools
- ✅ **Updated CI/CD** - Synchronized with local setup
- ✅ **Improved documentation** - Clear guides and examples

## 🎉 Current Status

- **All tests passing** - 145/145 ✅
- **Clean architecture** - No technical debt
- **Production ready** - Stable and tested
- **Well documented** - Clear guides for developers

## 🔮 Future Plans

- Enhanced error handling
- Additional resume formats
- Performance optimizations
- Extended LLM model support
