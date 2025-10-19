"""Tests for lizzy.helpers.terraform module."""

from unittest.mock import MagicMock, patch

import pytest

from lizzy.helpers.terraform import (
    create_slack_notification,
    get_headers,
    get_notifications,
    get_organization,
    get_request,
    get_workspaces,
    post_request,
    set_slack_webhook,
)


class TestGetOrganization:
    """Test get_organization function."""

    @patch("lizzy.helpers.terraform.get_setting")
    def test_get_organization_returns_org_name(self, mock_get_setting):
        """Test that get_organization returns the organization name."""
        mock_get_setting.return_value = "test-organization"

        result = get_organization()

        assert result == "test-organization"
        mock_get_setting.assert_called_once_with("terraform.organization")


class TestGetHeaders:
    """Test get_headers function."""

    @patch("lizzy.helpers.terraform.get_setting")
    def test_get_headers_returns_correct_format(self, mock_get_setting):
        """Test that get_headers returns properly formatted headers."""
        mock_get_setting.return_value = "test_token_123"

        result = get_headers()

        assert result == {
            "Authorization": "Bearer test_token_123",
            "Content-Type": "application/vnd.api+json",
        }
        mock_get_setting.assert_called_once_with("terraform.api_token")


class TestGetRequest:
    """Test get_request function."""

    @patch("lizzy.helpers.terraform.get_headers")
    @patch("lizzy.helpers.terraform.requests.get")
    def test_get_request_makes_request_with_headers(self, mock_get, mock_get_headers):
        """Test that get_request makes a GET request with proper headers."""
        mock_get_headers.return_value = {"Authorization": "Bearer token"}
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = get_request("https://api.terraform.io/test")

        assert result == mock_response
        mock_get.assert_called_once_with(
            "https://api.terraform.io/test", headers={"Authorization": "Bearer token"}
        )
        mock_response.raise_for_status.assert_called_once()

    @patch("lizzy.helpers.terraform.get_headers")
    @patch("lizzy.helpers.terraform.requests.get")
    def test_get_request_raises_on_error(self, mock_get, mock_get_headers):
        """Test that get_request raises exception on HTTP error."""
        mock_get_headers.return_value = {"Authorization": "Bearer token"}
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("HTTP 404")
        mock_get.return_value = mock_response

        with pytest.raises(Exception, match="HTTP 404"):
            get_request("https://api.terraform.io/test")


class TestPostRequest:
    """Test post_request function."""

    @patch("lizzy.helpers.terraform.get_headers")
    @patch("lizzy.helpers.terraform.requests.post")
    def test_post_request_makes_request_with_payload(self, mock_post, mock_get_headers):
        """Test that post_request makes a POST request with payload and headers."""
        mock_get_headers.return_value = {"Authorization": "Bearer token"}
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        payload = {"data": {"type": "test"}}
        result = post_request("https://api.terraform.io/test", payload)

        assert result == mock_response
        mock_post.assert_called_once_with(
            "https://api.terraform.io/test",
            json=payload,
            headers={"Authorization": "Bearer token"},
        )


class TestGetWorkspaces:
    """Test get_workspaces function."""

    @patch("lizzy.helpers.terraform.get_organization")
    @patch("lizzy.helpers.terraform.get_request")
    @patch("builtins.print")
    @patch("click.echo")
    def test_get_workspaces_returns_all_workspaces(
        self, mock_echo, mock_print, mock_get_request, mock_get_org
    ):
        """Test that get_workspaces returns all workspaces with pagination."""
        mock_get_org.return_value = "test-org"

        # First page response
        first_response = MagicMock()
        first_response.json.return_value = {
            "data": [{"id": "ws-1", "name": "workspace1"}],
            "links": {"next": "https://api.terraform.io/page2"},
        }

        # Second page response
        second_response = MagicMock()
        second_response.json.return_value = {
            "data": [{"id": "ws-2", "name": "workspace2"}],
            "links": {"next": None},
        }

        mock_get_request.side_effect = [first_response, second_response]

        result = get_workspaces()

        assert len(result) == 2
        assert result[0]["id"] == "ws-1"
        assert result[1]["id"] == "ws-2"
        assert mock_get_request.call_count == 2

    @patch("lizzy.helpers.terraform.get_organization")
    @patch("lizzy.helpers.terraform.get_request")
    @patch("builtins.print")
    def test_get_workspaces_handles_single_page(
        self, mock_print, mock_get_request, mock_get_org
    ):
        """Test that get_workspaces handles single page response."""
        mock_get_org.return_value = "test-org"

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [{"id": "ws-1", "name": "workspace1"}],
            "links": {"next": None},
        }

        mock_get_request.return_value = mock_response

        result = get_workspaces()

        assert len(result) == 1
        assert result[0]["id"] == "ws-1"
        assert mock_get_request.call_count == 1


class TestGetNotifications:
    """Test get_notifications function."""

    @patch("lizzy.helpers.terraform.get_request")
    def test_get_notifications_returns_notifications_list(self, mock_get_request):
        """Test that get_notifications returns the list of notifications."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {
                    "id": "ntf-1",
                    "attributes": {"destination-type": "slack", "enabled": True},
                }
            ]
        }
        mock_get_request.return_value = mock_response

        result = get_notifications("ws-123")

        assert len(result) == 1
        assert result[0]["id"] == "ntf-1"
        assert result[0]["attributes"]["destination-type"] == "slack"


class TestCreateSlackNotification:
    """Test create_slack_notification function."""

    @patch("lizzy.helpers.terraform.post_request")
    @patch("click.echo")
    def test_create_slack_notification_returns_true_on_success(
        self, mock_echo, mock_post_request
    ):
        """Test that create_slack_notification returns True when successful."""
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_post_request.return_value = mock_response

        result = create_slack_notification("ws-123", "https://hooks.slack.com/test")

        assert result is True
        mock_post_request.assert_called_once()

        # Verify payload structure
        call_args = mock_post_request.call_args[1]
        payload = call_args["json"]
        assert payload["data"]["type"] == "notification-configurations"
        assert payload["data"]["attributes"]["destination-type"] == "slack"
        assert payload["data"]["attributes"]["enabled"] is True
        assert payload["data"]["attributes"]["url"] == "https://hooks.slack.com/test"
        assert "run:created" in payload["data"]["attributes"]["triggers"]

    @patch("lizzy.helpers.terraform.post_request")
    @patch("click.echo")
    def test_create_slack_notification_returns_false_on_failure(
        self, mock_echo, mock_post_request
    ):
        """Test that create_slack_notification returns False on failure."""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_post_request.return_value = mock_response

        result = create_slack_notification("ws-123", "https://hooks.slack.com/test")

        assert result is False


class TestSetSlackWebhook:
    """Test set_slack_webhook function."""

    @patch("lizzy.helpers.terraform.get_setting")
    @patch("lizzy.helpers.terraform.get_workspaces")
    @patch("lizzy.helpers.terraform.get_notifications")
    @patch("lizzy.helpers.terraform.create_slack_notification")
    @patch("click.echo")
    def test_set_slack_webhook_adds_webhook_to_unconfigured_workspaces(
        self,
        mock_echo,
        mock_create_notification,
        mock_get_notifications,
        mock_get_workspaces,
        mock_get_setting,
    ):
        """Test that set_slack_webhook adds webhook to unconfigured workspaces."""
        mock_get_setting.return_value = "https://hooks.slack.com/test"

        mock_get_workspaces.return_value = [
            {"id": "ws-1", "attributes": {"name": "workspace1"}},
            {"id": "ws-2", "attributes": {"name": "workspace2"}},
        ]

        # First workspace has no slack notification, second has one
        mock_get_notifications.side_effect = [
            [{"attributes": {"destination-type": "email"}}],
            [{"attributes": {"destination-type": "slack"}}],
        ]

        mock_create_notification.return_value = True

        set_slack_webhook()

        # Should only create notification for first workspace
        mock_create_notification.assert_called_once_with(
            "ws-1", "https://hooks.slack.com/test"
        )

    @patch("lizzy.helpers.terraform.get_setting")
    def test_set_slack_webhook_raises_error_when_webhook_missing(
        self, mock_get_setting
    ):
        """Test that set_slack_webhook raises ValueError when webhook URL is missing."""
        mock_get_setting.return_value = None

        with pytest.raises(ValueError) as exc_info:
            set_slack_webhook()

        assert "Slack webhook URL is not set" in str(exc_info.value)

    @patch("lizzy.helpers.terraform.get_setting")
    @patch("lizzy.helpers.terraform.get_workspaces")
    @patch("lizzy.helpers.terraform.get_notifications")
    @patch("click.echo")
    def test_set_slack_webhook_skips_already_configured_workspaces(
        self, mock_echo, mock_get_notifications, mock_get_workspaces, mock_get_setting
    ):
        """Test that set_slack_webhook skips workspaces with existing slack config."""
        mock_get_setting.return_value = "https://hooks.slack.com/test"

        mock_get_workspaces.return_value = [
            {"id": "ws-1", "attributes": {"name": "workspace1"}}
        ]

        mock_get_notifications.return_value = [
            {"attributes": {"destination-type": "slack"}}
        ]

        set_slack_webhook()

        # Verify message about already configured was echoed
        echo_calls = [str(call) for call in mock_echo.call_args_list]
        assert any("already configured" in call for call in echo_calls)


class TestCancelRun:
    """Test cancel_run function."""

    @patch("lizzy.helpers.terraform.get_organization")
    @patch("lizzy.helpers.terraform.get_headers")
    @patch("lizzy.helpers.terraform.requests.post")
    @patch("click.echo")
    def test_cancel_run_discard_planned_success(self, mock_echo, mock_post, mock_get_headers, mock_get_org):
        """Test canceling a planned run with successful discard."""
        from lizzy.helpers.terraform import cancel_run
        
        mock_get_org.return_value = "test-org"
        mock_get_headers.return_value = {"Authorization": "Bearer token"}
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        cancel_run("run-123", "planned", "test-workspace")
        
        mock_post.assert_called_once_with(
            "https://app.terraform.io/api/v2/runs/run-123/actions/discard",
            headers={"Authorization": "Bearer token"}
        )
        mock_echo.assert_any_call("✅ Successfully discarded run run-123 (Status: planned)")

    @patch("lizzy.helpers.terraform.get_organization")
    @patch("lizzy.helpers.terraform.get_headers")
    @patch("lizzy.helpers.terraform.requests.post")
    @patch("click.echo")
    def test_cancel_run_discard_planned_initiated(self, mock_echo, mock_post, mock_get_headers, mock_get_org):
        """Test canceling a planned run with discard initiated."""
        from lizzy.helpers.terraform import cancel_run
        
        mock_get_org.return_value = "test-org"
        mock_get_headers.return_value = {"Authorization": "Bearer token"}
        mock_response = MagicMock()
        mock_response.status_code = 202  # Discard initiated
        mock_post.return_value = mock_response
        
        cancel_run("run-123", "planned", "test-workspace")
        
        mock_echo.assert_any_call("✅ Discard initiated for run run-123 (Status: planned)")

    @patch("lizzy.helpers.terraform.get_organization")
    @patch("lizzy.helpers.terraform.get_headers")
    @patch("lizzy.helpers.terraform.requests.post")
    @patch("click.echo")
    def test_cancel_run_discard_failed_attempt_cancel(self, mock_echo, mock_post, mock_get_headers, mock_get_org):
        """Test canceling a planned run when discard fails."""
        from lizzy.helpers.terraform import cancel_run
        
        mock_get_org.return_value = "test-org"
        mock_get_headers.return_value = {"Authorization": "Bearer token"}
        
        # Mock two calls: first fails (discard), second succeeds (cancel)
        mock_responses = [MagicMock(), MagicMock()]
        mock_responses[0].status_code = 400  # Discard fails
        mock_responses[1].status_code = 200  # Cancel succeeds
        mock_post.side_effect = mock_responses
        
        cancel_run("run-123", "planned", "test-workspace")
        
        assert mock_post.call_count == 2
        mock_echo.assert_any_call("⚠️  Failed to discard run run-123: 400. Attempting to cancel...")
        mock_echo.assert_any_call("✅ Successfully cancelled run run-123 (Status: planned)")

    @patch("lizzy.helpers.terraform.get_organization")
    @patch("lizzy.helpers.terraform.get_headers")
    @patch("lizzy.helpers.terraform.requests.post")
    @patch("click.echo")
    def test_cancel_run_non_planned_status(self, mock_echo, mock_post, mock_get_headers, mock_get_org):
        """Test canceling a run with non-planned status."""
        from lizzy.helpers.terraform import cancel_run
        
        mock_get_org.return_value = "test-org"
        mock_get_headers.return_value = {"Authorization": "Bearer token"}
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        cancel_run("run-123", "pending", "test-workspace")
        
        # Should skip discard and go directly to cancel
        mock_post.assert_called_once_with(
            "https://app.terraform.io/api/v2/runs/run-123/actions/cancel",
            headers={"Authorization": "Bearer token"}
        )
        mock_echo.assert_any_call("✅ Successfully cancelled run run-123 (Status: pending)")
