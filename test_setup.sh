#!/bin/bash
# Test setup verification script

echo "🦎 Lizzy CLI - Test Setup Verification"
echo "======================================"
echo ""

# Check if Python is installed
echo "✓ Checking Python installation..."
python3 --version || { echo "❌ Python not found"; exit 1; }
echo ""

# Check if pip is installed
echo "✓ Checking pip installation..."
pip --version || { echo "❌ pip not found"; exit 1; }
echo ""

# Install development dependencies
echo "✓ Installing development dependencies..."
pip install -r requirements-dev.txt -q || { echo "❌ Failed to install dependencies"; exit 1; }
echo ""

# Install the package
echo "✓ Installing lizzy package..."
pip install -e . -q || { echo "❌ Failed to install package"; exit 1; }
echo ""

# Run linting
echo "✓ Running linters..."
echo "  - flake8..."
flake8 lizzy/ commands/ --count --select=E9,F63,F7,F82 --show-source --statistics --exclude=venv,env,.git,__pycache__,.pytest_cache,build,dist,*.egg-info || { echo "❌ Linting failed"; exit 1; }
echo ""

# Run tests
echo "✓ Running tests..."
pytest tests/ -v --tb=short || { echo "❌ Tests failed"; exit 1; }
echo ""

# Generate coverage report
echo "✓ Generating coverage report..."
pytest tests/ --cov=lizzy --cov=commands --cov-report=term-missing --cov-report=html -q
echo ""

echo "======================================"
echo "✅ All checks passed!"
echo ""
echo "Coverage report available at: htmlcov/index.html"
echo "Run 'open htmlcov/index.html' to view"
echo ""
echo "🦎 Lizzy is ready to smash! 🦎"
