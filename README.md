# Lizzy CLI

![CI](https://github.com/Joeri-Abbo/lizzy/workflows/CI/badge.svg)
[![trivy](https://github.com/Joeri-Abbo/lizzy/actions/workflows/trivy.yml/badge.svg)](https://github.com/Joeri-Abbo/lizzy/actions/workflows/trivy.yml)
Lazzy jabbo cli - this tool is written for a lizard user 🦎 smash!

A command-line tool for managing AWS, GitLab, Datadog, and Terraform Cloud operations.

## Features

- **AWS Operations**:
  - Authenticate AWS CLI using account names
  - Manage ECS Fargate services and clusters
  - Force redeploy services and restart all services
- **GitLab Operations**:
  - Create merge requests (develop to main, main to develop)
  - Merge approved MRs
  - Remove merged branches
- **Datadog Management**:
  - Fetch Datadog agent versions
  - Bump Datadog components across repositories
- **Chef Integration**:
  - Update Chef environment versions
  - Manage Chef and Datadog component versions
- **Terraform Cloud**: 
  - Set up Slack webhooks for workspaces
  - Discard planned runs
- **Workflow Management**: Create and execute custom workflows
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
      { "name": "dev", "id": "123456789" },
      { "name": "prod", "id": "987654321" }
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
  "chef": {
    "chef_repo_owner": "your_org",
    "chef_repo_name": "chef-repo",
    "datadog_repo_owner": "DataDog",
    "datadog_repo_name": "datadog-agent"
  },
  "terraform": {
    "organization": "your_org",
    "api_token": "your_terraform_token",
    "slack_webhook_url": "https://hooks.slack.com/services/..."
  },
  "workflows": {
    "directory": "~/.lizzy/workflows"
  }
}
```

## Usage

### AWS Commands

```bash
# Authenticate with AWS account
lizzy aws auth <account_name>

# Restart Fargate service (interactive selection)
lizzy aws fargate-restart

# Restart all Fargate services in cluster
lizzy aws fargate-restart --all
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

# Discard planned runs
lizzy terraform-discard-plans
```

### Chef Commands

```bash
# Update Chef version in environment
lizzy chef modify-chef-version

# Update Datadog version in Chef environment
lizzy chef modify-datadog-version
```

### Workflow Commands

```bash
# Create a new workflow
lizzy workflows create

# List available workflows
lizzy workflows list

# Run a workflow (interactive selection if no name provided)
lizzy workflows run [workflow_name]
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

The project maintains high test coverage (85%+) with comprehensive unit tests for all major components:

- AWS operations (93% coverage)
- Chef integration (95% coverage)
- GitHub helpers (100% coverage)
- Workflow management (94% coverage)
- Configuration management (100% coverage)
- Datadog integration (99% coverage)

### Linting

```bash
# Check with ruff
ruff check .

# Auto-fix issues
ruff check . --fix

# Format code
ruff format .
```

### Code Quality

This project uses:

- **pytest** for testing
- **ruff** for linting and formatting (replaces black, flake8, pylint)
- **mypy** for type checking (optional)
- **pytest-cov** for coverage reporting

### Continuous Integration

GitHub Actions runs automated tests on:

- Python 3.9, 3.10, 3.11, 3.12
- Every push to master, main, develop
- Every pull request

See `.github/workflows/ci.yml` for details.

## Project Structure

```text
rocket-cli/
├── lizzy/              # Main package
│   ├── cli.py          # CLI interface
│   └── helpers/        # Helper modules
│       ├── aws.py      # AWS operations
│       ├── chef.py     # Chef operations
│       ├── config.py   # Configuration management
│       ├── datadog.py  # Datadog operations
│       ├── github.py   # GitHub operations
│       ├── gitlab.py   # GitLab operations
│       └── terraform.py # Terraform operations
├── commands/           # CLI command implementations
│   ├── aws_commands.py
│   ├── chef_commands.py
│   ├── datadog_commands.py
│   ├── gitlab_commands.py
│   ├── self_commands.py
│   └── workflows.py
├── tests/              # Unit tests (149 tests, 85% coverage)
│   ├── test_aws.py     # AWS operations tests
│   ├── test_chef.py    # Chef operations tests
│   ├── test_cli_commands.py # CLI command tests
│   ├── test_config.py  # Configuration tests
│   ├── test_datadog.py # Datadog tests
│   ├── test_github.py  # GitHub tests
│   ├── test_gitlab.py  # GitLab tests
│   ├── test_terraform.py # Terraform tests
│   └── test_workflows.py # Workflow tests
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

Joeri Abbo - [joeriabbo@hotmail.com](mailto:joeriabbo@hotmail.com)

## Support

For issues and questions, please open an issue on GitHub.
