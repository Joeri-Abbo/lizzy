# Tests

This directory contains unit tests for the lizzy CLI project.

## Running Tests

### Install Development Dependencies

```bash
pip install -r requirements-dev.txt
```

### Run All Tests

```bash
pytest
```

### Run Tests with Coverage

```bash
pytest --cov=lizzy --cov=commands --cov-report=term-missing
```

### Run Tests for a Specific Module

```bash
pytest tests/test_config.py
pytest tests/test_aws.py
pytest tests/test_datadog.py
pytest tests/test_gitlab.py
pytest tests/test_terraform.py
```

### Run Tests in Verbose Mode

```bash
pytest -v
```

### Run Tests and Generate HTML Coverage Report

```bash
pytest --cov=lizzy --cov=commands --cov-report=html
```

The HTML report will be generated in the `htmlcov` directory.

## Test Structure

- `test_config.py` - Tests for configuration management functions
- `test_aws.py` - Tests for AWS authentication and account management
- `test_datadog.py` - Tests for Datadog version management and component updates
- `test_gitlab.py` - Tests for GitLab operations (MRs, branch management)
- `test_terraform.py` - Tests for Terraform Cloud workspace management
- `conftest.py` - Pytest configuration and shared fixtures

## Writing Tests

Tests use:
- `pytest` as the test framework
- `unittest.mock` for mocking dependencies
- `pytest-cov` for coverage reporting

Each test module follows the pattern:
- Test classes group related tests (e.g., `TestGetAwsAccounts`)
- Test methods are named descriptively (e.g., `test_get_aws_accounts_returns_list`)
- Mocks are used to isolate unit tests from external dependencies

## Continuous Integration

Tests are automatically run on GitHub Actions for:
- Python versions: 3.9, 3.10, 3.11, 3.12
- On push to: master, main, develop branches
- On pull requests to these branches

See `.github/workflows/ci.yml` for the CI configuration.
