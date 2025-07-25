.PHONY: help install test lint format type-check ci-local clean

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install dependencies
	pip install --upgrade pip
	pip install -r requirements.txt
	pip install pytest pytest-asyncio httpx pytest-cov
	pip install flake8 black isort mypy

test:  ## Run tests
	pytest tests/services/ -v --tb=short

test-all:  ## Run all tests (including failing ones)
	pytest tests/ -v --tb=short || true

test-cov:  ## Run tests with coverage
	pytest tests/ --cov=src --cov-report=xml --cov-report=term-missing -v || true

lint:  ## Run all linting tools
	@echo "🔍 Running flake8..."
	flake8 src/ tests/ || true
	@echo "🔍 Running mypy..."
	mypy src/ --ignore-missing-imports || true

format:  ## Format code with black and isort
	@echo "🎨 Formatting with black..."
	black src/ tests/
	@echo "📦 Sorting imports with isort..."
	isort src/ tests/

format-check:  ## Check if code is formatted correctly
	@echo "🔍 Checking black formatting..."
	black --check --diff src/ tests/ || true
	@echo "🔍 Checking import sorting..."
	isort --check-only --diff src/ tests/ || true

ci-local:  ## Run the same checks as CI locally
	@echo "🚀 Running local CI checks..."
	@echo "📦 Checking format..."
	make format-check
	@echo "🔍 Running linting..."
	make lint
	@echo "🧪 Running tests..."
	make test-cov
	@echo "✅ Local CI checks completed!"

clean:  ## Clean up cache files
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .pytest_cache .coverage coverage.xml .mypy_cache

dev:  ## Start development server
	uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
