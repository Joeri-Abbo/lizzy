.PHONY: help install install-dev test test-cov lint format clean build

help:
	@echo "Lizzy CLI - Development Commands"
	@echo ""
	@echo "Available targets:"
	@echo "  install       - Install the package"
	@echo "  install-dev   - Install development dependencies"
	@echo "  test          - Run tests"
	@echo "  test-cov      - Run tests with coverage report"
	@echo "  lint          - Run all linters"
	@echo "  format        - Format code with black"
	@echo "  clean         - Clean build artifacts"
	@echo "  build         - Build the package"
	@echo "  ci            - Run CI checks (lint + test)"

install:
	pip install -e .

install-dev:
	pip install -r requirements-dev.txt
	pip install -e .

test:
	pytest -v

test-cov:
	pytest -v --cov=lizzy --cov=commands --cov-report=term-missing --cov-report=html

lint:
	@echo "Running ruff..."
	ruff check .

format:
	@echo "Formatting with ruff..."
	ruff check . --fix
	ruff format .

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete
	find . -type f -name '*.pyo' -delete

build: clean
	python setup.py sdist bdist_wheel

ci: lint test-cov
	@echo "CI checks completed successfully!"
