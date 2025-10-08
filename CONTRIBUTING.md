# Contributing to Lizzy CLI

Thank you for your interest in contributing to Lizzy CLI! 🦎

## Getting Started

### Prerequisites

- Python 3.9 or higher
- pip
- git

### Setting Up Development Environment

1. Fork and clone the repository:

```bash
git clone https://github.com/Joeri-Abbo/lizzy.git
cd lizzy
```

2. Install development dependencies:

```bash
pip install -r requirements-dev.txt
pip install -e .
```

Or use the Makefile:

```bash
make install-dev
```

3. Verify the setup:

```bash
./test_setup.sh
```

## Development Workflow

### Before Making Changes

1. Create a new branch:

```bash
git checkout -b feature/your-feature-name
```

2. Make sure all tests pass:

```bash
make test
```

### Making Changes

1. Write your code following the existing style
2. Add or update tests for your changes
3. Update documentation if needed

### Code Style

We use Ruff for code quality and formatting:

- **Ruff** - Fast Python linter and formatter (replaces black, flake8, pylint, isort)
- Line length: 88 characters
- Python 3.9+ compatible

Format your code:

```bash
make format
# or
ruff check . --fix
ruff format .
```

Check linting:

```bash
make lint
# or
ruff check .
```

### Writing Tests

- Place tests in the `tests/` directory
- Name test files as `test_<module>.py`
- Use descriptive test names: `test_<function>_<scenario>`
- Mock external dependencies (API calls, file system, etc.)
- Aim for high test coverage (>80%)

Example test structure:

```python
"""Tests for lizzy.module module."""
import pytest
from unittest.mock import patch, MagicMock
from lizzy.module import function_to_test


class TestFunctionToTest:
    """Test function_to_test."""

    @patch("lizzy.module.dependency")
    def test_function_returns_expected_value(self, mock_dependency):
        """Test that function_to_test returns the correct value."""
        mock_dependency.return_value = "expected"

        result = function_to_test()

        assert result == "expected"
        mock_dependency.assert_called_once()
```

### Running Tests

Run all tests:

```bash
pytest
# or
make test
```

Run with coverage:

```bash
pytest --cov=lizzy --cov=commands --cov-report=term-missing
# or
make test-cov
```

Run specific test file:

```bash
pytest tests/test_config.py
```

Run specific test:

```bash
pytest tests/test_config.py::TestGetSetting::test_get_setting_returns_nested_value
```

### Committing Changes

1. Make sure all tests pass:

```bash
make ci
```

2. Commit your changes with a descriptive message:

```bash
git add .
git commit -m "Add feature: description of your changes"
```

3. Push to your fork:

```bash
git push origin feature/your-feature-name
```

## Pull Request Process

1. Update the README.md with details of changes if applicable
2. Update tests to cover your changes
3. Ensure all CI checks pass
4. Write a clear PR description explaining:
   - What changes you made
   - Why you made them
   - Any breaking changes
   - Related issues

### PR Checklist

- [ ] Tests added/updated and passing
- [ ] Code follows the project style (black, flake8)
- [ ] Documentation updated
- [ ] Commit messages are clear and descriptive
- [ ] No merge conflicts

## Testing Guidelines

### Unit Tests

- Test individual functions in isolation
- Mock external dependencies
- Test both success and failure cases
- Test edge cases and boundary conditions

### Test Coverage

- Aim for at least 80% code coverage
- Focus on testing business logic
- Don't test external libraries

### Writing Good Tests

DO:

- ✅ Use descriptive test names
- ✅ Test one thing per test
- ✅ Mock external dependencies
- ✅ Use fixtures for common setup
- ✅ Test error conditions

DON'T:

- ❌ Test implementation details
- ❌ Write tests that depend on external services
- ❌ Make tests that are flaky
- ❌ Test third-party libraries

## Continuous Integration

Our CI pipeline runs on GitHub Actions and includes:

1. **Linting**: flake8, black, pylint
2. **Testing**: pytest on Python 3.9, 3.10, 3.11, 3.12
3. **Coverage**: Coverage reports uploaded to Codecov

All checks must pass before a PR can be merged.

## Project Structure

```
lizzy/
├── lizzy/              # Main package
│   ├── __init__.py
│   ├── cli.py          # CLI entry point
│   ├── config.py       # Configuration management
│   ├── aws.py          # AWS operations
│   ├── gitlab.py       # GitLab operations
│   ├── datadog.py      # Datadog operations
│   └── terraform.py    # Terraform operations
├── commands/           # CLI command implementations
├── tests/              # Unit tests
│   ├── __init__.py
│   ├── conftest.py     # Pytest configuration
│   ├── test_config.py
│   ├── test_aws.py
│   ├── test_gitlab.py
│   ├── test_datadog.py
│   └── test_terraform.py
└── .github/
    └── workflows/
        └── ci.yml      # CI configuration
```

## Need Help?

- Open an issue for bugs or feature requests
- Ask questions in pull requests
- Check existing issues and PRs first

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Help others learn and grow

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing to Lizzy CLI! 🦎✨
