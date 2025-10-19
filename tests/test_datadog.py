"""Tests for lizzy.helpers.datadog module."""

from unittest.mock import MagicMock, patch

import pytest

from lizzy.helpers.datadog import (
    bump_datadog_components,
    filter_content,
    get_auth_token,
    get_datadog_image,
    get_ecr_tags,
    get_fetch_versions,
    get_highest_version,
    print_fetch_versions,
)


class TestGetAuthToken:
    """Test get_auth_token function."""

    @patch("lizzy.helpers.datadog.requests.get")
    def test_get_auth_token_returns_token(self, mock_get):
        """Test that get_auth_token returns the authentication token."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"token": "test_token_123"}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = get_auth_token("datadog", "agent")

        assert result == "test_token_123"
        expected_url = (
            "https://public.ecr.aws/token/"
            "?service=public.ecr.aws&scope=repository:datadog/agent:pull"
        )
        mock_get.assert_called_once_with(expected_url)

    @patch("lizzy.helpers.datadog.requests.get")
    def test_get_auth_token_raises_on_error(self, mock_get):
        """Test that get_auth_token raises exception on HTTP error."""
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("HTTP 401")
        mock_get.return_value = mock_response

        with pytest.raises(Exception, match="HTTP 401"):
            get_auth_token("datadog", "agent")


class TestGetEcrTags:
    """Test get_ecr_tags function."""

    @patch("lizzy.helpers.datadog.get_auth_token")
    @patch("lizzy.helpers.datadog.requests.get")
    def test_get_ecr_tags_returns_all_tags(self, mock_get, mock_get_token):
        """Test that get_ecr_tags returns all tags with pagination."""
        mock_get_token.return_value = "test_token"

        # First page response
        first_response = MagicMock()
        first_response.json.return_value = {
            "tags": ["7.50.0", "7.50.1"],
            "next": "next_token_123",
        }
        first_response.raise_for_status = MagicMock()

        # Second page response
        second_response = MagicMock()
        second_response.json.return_value = {"tags": ["7.50.2"], "next": None}
        second_response.raise_for_status = MagicMock()

        mock_get.side_effect = [first_response, second_response]

        result = get_ecr_tags("datadog", "agent")

        assert result == ["7.50.0", "7.50.1", "7.50.2"]
        assert mock_get.call_count == 2

    @patch("lizzy.helpers.datadog.get_auth_token")
    @patch("lizzy.helpers.datadog.requests.get")
    def test_get_ecr_tags_handles_single_page(self, mock_get, mock_get_token):
        """Test that get_ecr_tags handles single page response."""
        mock_get_token.return_value = "test_token"

        mock_response = MagicMock()
        mock_response.json.return_value = {"tags": ["7.50.0", "7.50.1"], "next": None}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = get_ecr_tags("datadog", "agent")

        assert result == ["7.50.0", "7.50.1"]
        assert mock_get.call_count == 1


class TestGetFetchVersions:
    """Test get_fetch_versions function."""

    @patch("lizzy.helpers.datadog.get_ecr_tags")
    def test_get_fetch_versions_filters_semantic_versions(self, mock_get_tags):
        """Test that get_fetch_versions filters out non-semantic version tags."""
        mock_get_tags.return_value = [
            "7.50.0",
            "7.50.1",
            "7.50.2-rc1",
            "latest",
            "7.49.0",
            "invalid-tag",
            "7.51.0",
        ]

        result = get_fetch_versions()

        assert "7.50.0" in result
        assert "7.50.1" in result
        assert "7.49.0" in result
        assert "7.51.0" in result
        assert "7.50.2-rc1" not in result
        assert "latest" not in result
        assert "invalid-tag" not in result


class TestPrintFetchVersions:
    """Test print_fetch_versions function."""

    @patch("lizzy.helpers.datadog.get_fetch_versions")
    @patch("click.echo")
    def test_print_fetch_versions_displays_sorted_versions(
        self, mock_echo, mock_get_versions
    ):
        """Test that print_fetch_versions displays versions in sorted order."""
        mock_get_versions.return_value = ["7.50.1", "7.49.0", "7.51.0"]

        print_fetch_versions()

        # Verify all versions were echoed
        assert mock_echo.call_count == 3
        calls = [str(call[0][0]) for call in mock_echo.call_args_list]
        assert "Datadog Agent: 7.49.0" in calls
        assert "Datadog Agent: 7.50.1" in calls
        assert "Datadog Agent: 7.51.0" in calls


class TestGetHighestVersion:
    """Test get_highest_version function."""

    @patch("lizzy.helpers.datadog.get_fetch_versions")
    def test_get_highest_version_returns_latest(self, mock_get_versions):
        """Test that get_highest_version returns the highest semantic version."""
        mock_get_versions.return_value = ["7.49.0", "7.50.1", "7.50.0", "7.51.0"]

        result = get_highest_version()

        assert result == "7.51.0"

    @patch("lizzy.helpers.datadog.get_fetch_versions")
    def test_get_highest_version_handles_single_version(self, mock_get_versions):
        """Test that get_highest_version handles single version."""
        mock_get_versions.return_value = ["7.50.0"]

        result = get_highest_version()

        assert result == "7.50.0"


class TestFilterContent:
    """Test filter_content function."""

    def test_filter_content_removes_jsonencode_prefix(self):
        """Test that filter_content removes jsonencode prefix."""
        content = "${jsonencode(test content)}"
        result = filter_content(content)
        assert result == "test content"

    def test_filter_content_removes_suffix(self):
        """Test that filter_content removes closing parenthesis and brace."""
        content = "test content)}"
        result = filter_content(content)
        assert result == "test content"

    def test_filter_content_removes_comments(self):
        """Test that filter_content removes comments."""
        content = "test content # this is a comment"
        result = filter_content(content)
        assert "# this is a comment" not in result

    def test_filter_content_strips_whitespace(self):
        """Test that filter_content strips leading/trailing whitespace."""
        content = "  test content  "
        result = filter_content(content)
        assert result == "test content"


class TestGetDatadogImage:
    """Test get_datadog_image function."""

    def test_get_datadog_image_finds_agent_image(self):
        """Test that get_datadog_image finds the datadog-agent image."""
        items = [
            {"name": "app", "image": "app:latest"},
            {
                "name": "datadog-agent",
                "image": "580117755768.dkr.ecr.eu-central-1.amazonaws.com/public.ecr.aws/datadog/agent:7.50.0",
            },
            {"name": "sidecar", "image": "sidecar:1.0"},
        ]

        with patch("lizzy.helpers.datadog.filter_content", side_effect=lambda x: x):
            result = get_datadog_image(items)

        assert "datadog/agent:7.50.0" in result

    def test_get_datadog_image_returns_empty_when_not_found(self):
        """Test that get_datadog_image returns empty string when not found."""
        items = [
            {"name": "app", "image": "app:latest"},
            {"name": "sidecar", "image": "sidecar:1.0"},
        ]

        result = get_datadog_image(items)

        assert result == ""


class TestBumpDatadogComponents:
    """Test bump_datadog_components function."""

    @patch("lizzy.helpers.datadog.get_setting")
    @patch("lizzy.helpers.datadog.setup_gitlab")
    @patch("click.echo")
    def test_bump_datadog_components_processes_all_components(
        self, mock_echo, mock_gitlab, mock_get_setting
    ):
        """Test that bump_datadog_components processes all components."""
        mock_get_setting.side_effect = lambda key: {
            "gitlab.components": [
                {
                    "name": "test-component",
                    "project_name_with_namespace": "group/project",
                    "branch": "develop",
                }
            ],
            "gitlab.username": "testuser",
            "gitlab.email": "test@example.com",
        }.get(key)

        mock_gl = MagicMock()
        mock_gitlab.return_value = mock_gl

        mock_project = MagicMock()
        mock_gl.projects.get.return_value = mock_project

        mock_file = MagicMock()
        mock_file.decode.return_value.decode.return_value = '${jsonencode([{"name": "datadog-agent", "image": "datadog/agent:7.49.0"}])}'
        mock_project.files.get.return_value = mock_file

        mock_project.branches.create = MagicMock()
        mock_project.commits.create = MagicMock()
        mock_project.mergerequests.create = MagicMock(
            return_value=MagicMock(web_url="https://gitlab.com/mr/1")
        )

        bump_datadog_components("7.50.0")

        mock_gl.projects.get.assert_called_once()
        mock_project.branches.create.assert_called_once()
        mock_project.commits.create.assert_called_once()
        mock_project.mergerequests.create.assert_called_once()

    @patch("lizzy.helpers.datadog.get_setting")
    @patch("lizzy.helpers.datadog.setup_gitlab")
    @patch("click.echo")
    def test_bump_datadog_components_handles_errors(
        self, mock_echo, mock_gitlab, mock_get_setting
    ):
        """Test that bump_datadog_components handles errors gracefully."""
        mock_get_setting.side_effect = lambda key: {
            "gitlab.components": [
                {
                    "name": "test-component",
                    "project_name_with_namespace": "group/project",
                    "branch": "develop",
                }
            ],
            "gitlab.username": "testuser",
            "gitlab.email": "test@example.com",
        }.get(key)

        mock_gl = MagicMock()
        mock_gitlab.return_value = mock_gl
        mock_gl.projects.get.side_effect = Exception("Project not found")

        bump_datadog_components("7.50.0")

        # Verify error was echoed
        error_calls = [
            call for call in mock_echo.call_args_list if "Failed" in str(call)
        ]
        assert len(error_calls) > 0
