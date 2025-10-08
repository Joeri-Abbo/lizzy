# Lizzy CLI

![CI](https://github.com/Joeri-Abbo/lizzy/workflows/CI/badge.svg)
[![codecov](https://codecov.io/gh/Joeri-Abbo/lizzy/branch/master/graph/badge.svg)](https://codecov.io/gh/Joeri-Abbo/lizzy)

Lazzy jabbo cli - this tool is written for a lizard user 🦎 smash!

A command-line tool for managing AWS, GitLab, Datadog, and Terraform Cloud operations.

## Features

- **AWS Authentication**: Authenticate AWS CLI using account names
- **GitLab Operations**: 
  - Create merge requests (develop to main, main to develop)
  - Merge approved MRs
  - Remove merged branches
- **Datadog Management**:
  - Fetch Datadog agent versions
  - Bump Datadog components across repositories
- **Terraform Cloud**: Set up Slack webhooks for workspaces
- **Configuration Management**: Easy config file management with vim

## Installation

### From Source

```bash
git clone https://github.com/Joeri-Abbo/lizzy.git
cd lizzy
pip install -e .
```

### Quick Install Script

```bash
./install.sh
```

## Configuration

On first run, Lizzy will create a config file at `~/.lizzy/config.json`.

Edit your configuration:

```bash
lizzy config edit
```

### Configuration Structure

```json
{
  "aws": {
    "accounts": [
      {"name": "dev", "id": "123456789"},
      {"name": "prod", "id": "987654321"}
    ]
  },
  "gitlab": {
    "api_token": "your_gitlab_token",
    "username": "your_username",
    "email": "your_email@example.com",
    "approval_group_id": "group_id",
    "components": [
      {
        "name": "component1",
        "project_name_with_namespace": "group/project",
        "branch": "develop"
      }
    ]
  },
  "terraform": {
    "organization": "your_org",
    "api_token": "your_terraform_token",
    "slack_webhook_url": "https://hooks.slack.com/services/..."
  }
}
```

## Usage

### AWS Commands

```bash
# Authenticate with AWS account
lizzy aws auth <account_name>
```

### GitLab Commands

```bash
# Create merge requests from develop to main
lizzy gitlab develop-to-main

# Create merge requests from main to develop
lizzy gitlab main-to-develop

# Merge approved merge requests
lizzy gitlab merge-approved

# Merge approved merge requests without confirmation (YOLO mode)
lizzy gitlab merge-approved --yolo

# Remove merged branches from all projects
lizzy gitlab remove-merged-branches
```

### Datadog Commands

```bash
# Fetch all available Datadog versions
lizzy datadog fetch-versions

# Get the latest Datadog version
lizzy datadog fetch-version-latest

# Bump Datadog components to a specific version
lizzy datadog bump-components <version>

# Bump Datadog components to the latest version
lizzy datadog bump-components-latest
```

### Terraform Commands

```bash
# Set Slack webhook for all Terraform workspaces
lizzy terraform set-slack-webhook
```

### Configuration Commands

```bash
# Edit configuration file
lizzy config edit
```

## Development

### Install Development Dependencies

```bash
pip install -r requirements-dev.txt
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=lizzy --cov=commands --cov-report=term-missing

# Run specific test file
pytest tests/test_config.py

# Run in verbose mode
pytest -v
```

### Linting

```bash
# Check with flake8
flake8 lizzy/ commands/ tests/

# Format with black
black lizzy/ commands/ tests/

# Lint with pylint
pylint lizzy/ commands/
```

### Code Quality

This project uses:
- **pytest** for testing
- **black** for code formatting
- **flake8** for linting
- **pylint** for static analysis
- **mypy** for type checking (optional)
- **pytest-cov** for coverage reporting

### Continuous Integration

GitHub Actions runs automated tests on:
- Python 3.9, 3.10, 3.11, 3.12
- Every push to master, main, develop
- Every pull request

See `.github/workflows/ci.yml` for details.

## Project Structure

```
rocket-cli/
├── lizzy/              # Main package
│   ├── aws.py          # AWS operations
│   ├── config.py       # Configuration management
│   ├── datadog.py      # Datadog operations
│   ├── gitlab.py       # GitLab operations
│   ├── terraform.py    # Terraform operations
│   └── cli.py          # CLI interface
├── commands/           # CLI command implementations
├── tests/              # Unit tests
│   ├── test_aws.py
│   ├── test_config.py
│   ├── test_datadog.py
│   ├── test_gitlab.py
│   └── test_terraform.py
├── .github/
│   └── workflows/
│       └── ci.yml      # CI/CD configuration
├── setup.py            # Package configuration
├── pyproject.toml      # Tool configuration
└── requirements-dev.txt # Development dependencies
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

MIT License

## Author

Joeri Abbo - jabbo@schubergphilis.com

## Support

For issues and questions, please open an issue on GitHub.
