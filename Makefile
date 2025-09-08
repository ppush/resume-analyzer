.PHONY: help install install-dev format lint type-check test test-cov clean quality-check pre-commit-install

help: ## Show help
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install main dependencies
	pip install -r requirements.txt

install-dev: ## Install development dependencies
	pip install -r requirements-dev.txt

format: ## Format code (black + isort)
	black .
	isort .

lint: ## Check code style (flake8)
	flake8 .

type-check: ## Check types (mypy)
	mypy core/ services/

test: ## Run tests
	python tests/run_all_tests.py

test-pytest: ## Run tests via pytest
	pytest tests/ -v

test-async: ## Run async tests via pytest
	pytest tests/ -v --asyncio-mode=auto

test-cov: ## Run tests with coverage
	python tests/run_all_tests.py

quality-check: format lint type-check test ## Full code quality check

quality-check-full: ## Full quality check with additional checks
	@echo "Quality check script removed - use individual commands instead"

pre-commit-install: ## Install pre-commit hooks
	@echo "Pre-commit hooks removed - use individual quality commands instead"

clean: ## Clean temporary files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +

setup-dev: install-dev pre-commit-install ## Setup development environment

ci: quality-check ## Command for CI/CD pipeline
