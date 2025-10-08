"""Pytest configuration and fixtures for lizzy tests."""

import sys
from pathlib import Path

import pytest

# Add the project root to the path so imports work correctly
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def sample_aws_accounts():
    """Fixture providing sample AWS account data."""
    return [
        {"name": "dev", "id": "123456789"},
        {"name": "staging", "id": "234567890"},
        {"name": "prod", "id": "345678901"},
    ]


@pytest.fixture
def sample_config():
    """Fixture providing sample configuration data."""
    return {
        "aws": {
            "accounts": [
                {"name": "dev", "id": "123456789"},
                {"name": "prod", "id": "987654321"},
            ]
        },
        "gitlab": {
            "api_token": "test_token",
            "username": "testuser",
            "email": "test@example.com",
            "approval_group_id": "group_123",
            "components": [
                {
                    "name": "component1",
                    "project_name_with_namespace": "group/project1",
                    "branch": "develop",
                }
            ],
        },
        "terraform": {
            "organization": "test-org",
            "api_token": "terraform_token",
            "slack_webhook_url": "https://hooks.slack.com/test",
        },
    }


@pytest.fixture
def sample_datadog_versions():
    """Fixture providing sample Datadog versions."""
    return ["7.49.0", "7.49.1", "7.50.0", "7.50.1", "7.51.0"]


@pytest.fixture
def sample_gitlab_merge_request():
    """Fixture providing a sample GitLab merge request."""
    return {
        "iid": 1,
        "title": "Test MR",
        "web_url": "https://gitlab.com/mr/1",
        "source_branch": "feature/test",
        "target_branch": "develop",
        "author": {"username": "testuser"},
    }
