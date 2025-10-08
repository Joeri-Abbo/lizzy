# Test Setup Checklist

Use this checklist to verify and complete the test setup for Lizzy CLI.

## Initial Setup ✅

- [x] Created `.github/workflows/ci.yml` for GitHub Actions
- [x] Created `tests/` directory with all test files
- [x] Created `requirements-dev.txt` with development dependencies
- [x] Created `pyproject.toml` with tool configurations
- [x] Created `Makefile` for common development tasks
- [x] Created `test_setup.sh` verification script
- [x] Updated `README.md` with testing documentation
- [x] Created `CONTRIBUTING.md` with contribution guidelines

## Test Files Created ✅

- [x] `tests/__init__.py` - Package initialization
- [x] `tests/conftest.py` - Pytest fixtures and configuration
- [x] `tests/test_config.py` - Tests for configuration management
- [x] `tests/test_aws.py` - Tests for AWS operations
- [x] `tests/test_datadog.py` - Tests for Datadog operations
- [x] `tests/test_gitlab.py` - Tests for GitLab operations
- [x] `tests/test_terraform.py` - Tests for Terraform operations

## Next Steps (Manual)

### 1. Install Dependencies and Run Tests

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Install the package in development mode
pip install -e .

# Run the verification script
./test_setup.sh
```

### 2. Fix Any Import Errors

If you see import errors when running tests, you may need to:

- Ensure all dependencies are installed
- Check that the package is installed in development mode
- Verify Python path is set correctly

### 3. Configure GitHub Actions

To enable GitHub Actions:

1. Push the code to GitHub:
   ```bash
   git add .
   git commit -m "Add testing infrastructure and GitHub Actions CI"
   git push origin master
   ```

2. Go to your GitHub repository
3. Click on "Actions" tab
4. Enable workflows if prompted
5. The CI will run automatically on the next push

### 4. Set Up Codecov (Optional)

For coverage reporting:

1. Go to [codecov.io](https://codecov.io)
2. Sign in with GitHub
3. Add your repository
4. Get your Codecov token
5. Add it as a GitHub Secret:
   - Repository Settings → Secrets → Actions
   - Add secret: `CODECOV_TOKEN`

### 5. Update README Badges

In `README.md`, update these lines with your actual GitHub username:

```markdown
![CI](https://github.com/YOUR_USERNAME/lizzy/workflows/CI/badge.svg)
[![codecov](https://codecov.io/gh/YOUR_USERNAME/lizzy/branch/master/graph/badge.svg)](https://codecov.io/gh/YOUR_USERNAME/lizzy)
```

Replace `YOUR_USERNAME` with `Joeri-Abbo` (or your actual GitHub username).

### 6. Verify CI Pipeline

After pushing to GitHub:

1. Go to Actions tab
2. Watch the CI run
3. Verify both lint and test jobs pass
4. Check coverage report on Codecov (if configured)

### 7. Run Local Tests

Before each commit:

```bash
# Format code
make format

# Run linters
make lint

# Run tests
make test

# Or run everything
make ci
```

### 8. Add Tests for Commands

The current tests cover the helper functions in `lizzy/`. You may want to add tests for:

- `commands/aws_authenticate.py`
- `commands/config_edit.py`
- `commands/datadog_*.py`
- `commands/gitlab_*.py`
- `commands/terraform_*.py`

Example structure for command tests:

```python
# tests/test_commands_aws.py
"""Tests for commands.aws_authenticate module."""
import pytest
from unittest.mock import patch
from commands.aws_authenticate import authenticate

class TestAuthenticate:
    @patch("commands.aws_authenticate.get_aws_credentials")
    def test_authenticate_success(self, mock_get_creds):
        # Test implementation
        pass
```

## Verification Checklist

Run these commands to verify everything works:

- [ ] `python --version` (Should be 3.9+)
- [ ] `pip install -r requirements-dev.txt` (Should install without errors)
- [ ] `pip install -e .` (Should install lizzy package)
- [ ] `pytest --version` (Should show pytest version)
- [ ] `pytest tests/` (Should run all tests)
- [ ] `pytest --cov=lizzy --cov-report=term-missing` (Should show coverage report)
- [ ] `make test` (Should run tests via Makefile)
- [ ] `make lint` (Should check code quality)
- [ ] `make format` (Should format code)
- [ ] `./test_setup.sh` (Should complete successfully)

## Common Issues and Solutions

### Issue: Import errors when running tests

**Solution**: Make sure you've installed the package in development mode:
```bash
pip install -e .
```

### Issue: Missing dependencies

**Solution**: Install all development dependencies:
```bash
pip install -r requirements-dev.txt
```

### Issue: Tests fail due to missing configuration

**Solution**: Tests use mocks and shouldn't require actual configuration. Check that mocks are properly set up in the test file.

### Issue: CI fails on GitHub Actions

**Solution**: 
1. Check the Actions log for specific errors
2. Ensure all dependencies are listed in `requirements-dev.txt`
3. Verify the workflow file syntax is correct

### Issue: Coverage too low

**Solution**: Add more tests to cover untested code paths. Use `pytest --cov=lizzy --cov-report=html` to see which lines aren't covered.

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [GitHub Actions docs](https://docs.github.com/en/actions)
- [Codecov docs](https://docs.codecov.com/)
- [unittest.mock guide](https://docs.python.org/3/library/unittest.mock.html)

## Success Criteria

✅ All tests pass locally
✅ Coverage is above 80%
✅ All linters pass (flake8, black, pylint)
✅ CI pipeline passes on GitHub
✅ Documentation is complete and up-to-date

---

**Last Updated**: 2025-10-08

**Status**: Ready for testing 🦎
