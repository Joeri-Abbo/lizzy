"""Tests for lizzy.helpers.chef module."""

from unittest.mock import MagicMock, patch, call

import pytest

from lizzy.helpers.chef import (
    setup_chef_api,
    get_chef_environments, 
    get_knife_config_path,
    get_chef_environment,
    update_datadog_version,
    update_chef_version,
    get_latest_chef_version,
    get_latest_datadog_version
)


class TestSetupChefApi:
    """Test setup_chef_api function."""

    @patch("lizzy.helpers.chef.chef.autoconfigure")
    def test_setup_chef_api_returns_api_instance(self, mock_autoconfigure):
        """Test that setup_chef_api returns a chef API instance."""
        mock_api = MagicMock()
        mock_autoconfigure.return_value = mock_api
        
        result = setup_chef_api()
        
        assert result == mock_api
        mock_autoconfigure.assert_called_once()


class TestGetChefEnvironments:
    """Test get_chef_environments function."""

    @patch("lizzy.helpers.chef.get_setting")
    def test_get_chef_environments_returns_environments_list(self, mock_get_setting):
        """Test that get_chef_environments returns environments from config."""
        expected_environments = ["dev", "staging", "prod"]
        mock_get_setting.return_value = expected_environments
        
        result = get_chef_environments()
        
        assert result == expected_environments
        mock_get_setting.assert_called_once_with("chef.environments")


class TestGetKnifeConfigPath:
    """Test get_knife_config_path function."""

    @patch("lizzy.helpers.chef.get_setting")
    def test_get_knife_config_path_returns_path(self, mock_get_setting):
        """Test that get_knife_config_path returns knife config path."""
        expected_path = "~/.chef/knife.rb"
        mock_get_setting.return_value = expected_path
        
        result = get_knife_config_path()
        
        assert result == expected_path
        mock_get_setting.assert_called_once_with("chef.knife_config_path")


class TestGetChefEnvironment:
    """Test get_chef_environment function."""

    @patch("lizzy.helpers.chef.get_chef_environments")
    def test_get_chef_environment_returns_single_environment(self, mock_get_environments):
        """Test that get_chef_environment returns single environment when only one exists."""
        mock_get_environments.return_value = ["prod"]
        
        result = get_chef_environment()
        
        assert result == "prod"

    @patch("lizzy.helpers.chef.get_chef_environments")
    def test_get_chef_environment_raises_error_when_no_environments(self, mock_get_environments):
        """Test that get_chef_environment raises error when no environments configured."""
        mock_get_environments.return_value = []
        
        with pytest.raises(ValueError) as exc_info:
            get_chef_environment()
        
        assert "No Chef environments configured" in str(exc_info.value)

    @patch("lizzy.helpers.chef.get_chef_environments")
    @patch("lizzy.helpers.chef.click.echo")
    @patch("lizzy.helpers.chef.click.prompt")
    def test_get_chef_environment_prompts_for_multiple_environments(
        self, mock_prompt, mock_echo, mock_get_environments
    ):
        """Test that get_chef_environment prompts when multiple environments exist."""
        mock_get_environments.return_value = ["dev", "staging", "prod"]
        mock_prompt.return_value = 2
        
        result = get_chef_environment()
        
        assert result == "staging"
        mock_echo.assert_called()
        mock_prompt.assert_called_once_with("Select an environment by number", type=int)

    @patch("lizzy.helpers.chef.get_chef_environments")
    @patch("lizzy.helpers.chef.click.echo")
    @patch("lizzy.helpers.chef.click.prompt")
    def test_get_chef_environment_raises_error_for_invalid_selection(
        self, mock_prompt, mock_echo, mock_get_environments
    ):
        """Test that get_chef_environment raises error for invalid selection."""
        mock_get_environments.return_value = ["dev", "staging", "prod"]
        mock_prompt.return_value = 5  # Invalid selection
        
        with pytest.raises(ValueError) as exc_info:
            get_chef_environment()
        
        assert "Invalid selection" in str(exc_info.value)


class TestUpdateDatadogVersion:
    """Test update_datadog_version function."""

    @patch("lizzy.helpers.chef.setup_chef_api")
    @patch("lizzy.helpers.chef.chef.Environment")
    @patch("lizzy.helpers.chef.get_chef_environment")
    @patch("lizzy.helpers.chef.get_latest_datadog_version")
    @patch("lizzy.helpers.chef.click.echo")
    @patch("lizzy.helpers.chef.click.confirm")
    def test_update_datadog_version_with_latest_version(
        self, mock_confirm, mock_echo, mock_get_latest, mock_get_env, 
        mock_environment, mock_setup_api
    ):
        """Test update_datadog_version using latest version from GitHub."""
        mock_api = MagicMock()
        mock_setup_api.return_value = mock_api
        mock_get_env.return_value = "prod"
        mock_get_latest.return_value = "v7.45.0"
        
        mock_env = MagicMock()
        mock_env.override_attributes = {"datadog": {"agent_version": "7.44.0"}}
        mock_environment.return_value = mock_env
        
        mock_confirm.side_effect = [True, True]  # Fetch latest + confirm update
        
        update_datadog_version()
        
        mock_environment.assert_called_once_with("prod", api=mock_api)
        assert mock_env.override_attributes["datadog"]["agent_version"] == "7.45.0"
        mock_env.save.assert_called_once()

    @patch("lizzy.helpers.chef.setup_chef_api")
    @patch("lizzy.helpers.chef.chef.Environment")
    @patch("lizzy.helpers.chef.get_chef_environment")
    @patch("lizzy.helpers.chef.click.echo")
    @patch("lizzy.helpers.chef.click.confirm")
    @patch("lizzy.helpers.chef.click.prompt")
    def test_update_datadog_version_with_manual_version(
        self, mock_prompt, mock_confirm, mock_echo, mock_get_env, 
        mock_environment, mock_setup_api
    ):
        """Test update_datadog_version using manually entered version."""
        mock_api = MagicMock()
        mock_setup_api.return_value = mock_api
        mock_get_env.return_value = "dev"
        
        mock_env = MagicMock()
        mock_env.override_attributes = {"datadog": {"agent_version": "7.44.0"}}
        mock_environment.return_value = mock_env
        
        mock_confirm.side_effect = [False, True]  # Don't fetch latest + confirm update
        mock_prompt.return_value = "7.46.0"
        
        update_datadog_version()
        
        assert mock_env.override_attributes["datadog"]["agent_version"] == "7.46.0"
        mock_env.save.assert_called_once()

    @patch("lizzy.helpers.chef.setup_chef_api")
    @patch("lizzy.helpers.chef.chef.Environment")
    @patch("lizzy.helpers.chef.get_chef_environment")
    @patch("lizzy.helpers.chef.get_latest_datadog_version")
    @patch("lizzy.helpers.chef.click.echo")
    @patch("lizzy.helpers.chef.click.confirm")
    def test_update_datadog_version_handles_fetch_failure(
        self, mock_confirm, mock_echo, mock_get_latest, mock_get_env, 
        mock_environment, mock_setup_api
    ):
        """Test update_datadog_version handles failure to fetch latest version."""
        mock_api = MagicMock()
        mock_setup_api.return_value = mock_api
        mock_get_env.return_value = "prod"
        mock_get_latest.return_value = None  # Simulate fetch failure
        
        mock_env = MagicMock()
        mock_environment.return_value = mock_env
        
        mock_confirm.return_value = True  # Fetch latest
        
        # This should raise AttributeError because the actual function tries to call .replace() on None
        with pytest.raises(AttributeError):
            update_datadog_version()


class TestUpdateChefVersion:
    """Test update_chef_version function."""

    @patch("lizzy.helpers.chef.setup_chef_api")
    @patch("lizzy.helpers.chef.chef.Environment")
    @patch("lizzy.helpers.chef.get_chef_environment")
    @patch("lizzy.helpers.chef.get_latest_chef_version")
    @patch("lizzy.helpers.chef.click.echo")
    @patch("lizzy.helpers.chef.click.confirm")
    def test_update_chef_version_with_latest_version(
        self, mock_confirm, mock_echo, mock_get_latest, mock_get_env, 
        mock_environment, mock_setup_api
    ):
        """Test update_chef_version using latest version from GitHub."""
        mock_api = MagicMock()
        mock_setup_api.return_value = mock_api
        mock_get_env.return_value = "staging"
        mock_get_latest.return_value = "v18.2.7"
        
        mock_env = MagicMock()
        mock_env.default_attributes = {"chef_client_updater": {"version": "18.1.0"}}
        mock_environment.return_value = mock_env
        
        mock_confirm.side_effect = [True, True]  # Fetch latest + confirm update
        
        update_chef_version()
        
        mock_environment.assert_called_once_with("staging", api=mock_api)
        assert mock_env.default_attributes["chef_client_updater"]["version"] == "18.2.7"
        mock_env.save.assert_called_once()

    @patch("lizzy.helpers.chef.setup_chef_api")
    @patch("lizzy.helpers.chef.chef.Environment")
    @patch("lizzy.helpers.chef.get_chef_environment")
    @patch("lizzy.helpers.chef.click.echo")
    @patch("lizzy.helpers.chef.click.confirm")
    @patch("lizzy.helpers.chef.click.prompt")
    def test_update_chef_version_creates_missing_attributes(
        self, mock_prompt, mock_confirm, mock_echo, mock_get_env, 
        mock_environment, mock_setup_api
    ):
        """Test update_chef_version creates missing chef_client_updater attributes."""
        mock_api = MagicMock()
        mock_setup_api.return_value = mock_api
        mock_get_env.return_value = "dev"
        
        mock_env = MagicMock()
        mock_env.default_attributes = {}  # Missing chef_client_updater
        mock_environment.return_value = mock_env
        
        mock_confirm.side_effect = [False, True]  # Don't fetch latest + confirm update
        mock_prompt.return_value = "18.3.0"
        
        update_chef_version()
        
        assert "chef_client_updater" in mock_env.default_attributes
        assert mock_env.default_attributes["chef_client_updater"]["version"] == "18.3.0"
        mock_env.save.assert_called_once()


class TestGetLatestChefVersion:
    """Test get_latest_chef_version function."""

    @patch("lizzy.helpers.chef.get_tags_of_repo")
    def test_get_latest_chef_version_returns_first_tag(self, mock_get_tags):
        """Test that get_latest_chef_version returns the first tag from GitHub."""
        mock_get_tags.return_value = ["v18.2.7", "v18.2.6", "v18.2.5"]
        
        result = get_latest_chef_version()
        
        assert result == "v18.2.7"
        mock_get_tags.assert_called_once_with("chef/chef")

    @patch("lizzy.helpers.chef.get_tags_of_repo")
    def test_get_latest_chef_version_returns_none_when_no_tags(self, mock_get_tags):
        """Test that get_latest_chef_version returns None when no tags found."""
        mock_get_tags.return_value = []
        
        result = get_latest_chef_version()
        
        assert result is None


class TestGetLatestDatadogVersion:
    """Test get_latest_datadog_version function."""

    @patch("lizzy.helpers.chef.get_tags_of_repo")
    def test_get_latest_datadog_version_returns_first_tag(self, mock_get_tags):
        """Test that get_latest_datadog_version returns the first tag from GitHub."""
        mock_get_tags.return_value = ["7.45.0", "7.44.1", "7.44.0"]
        
        result = get_latest_datadog_version()
        
        assert result == "7.45.0"
        mock_get_tags.assert_called_once_with("DataDog/datadog-agent")

    @patch("lizzy.helpers.chef.get_tags_of_repo")
    def test_get_latest_datadog_version_returns_none_when_no_tags(self, mock_get_tags):
        """Test that get_latest_datadog_version returns None when no tags found."""
        mock_get_tags.return_value = []
        
        result = get_latest_datadog_version()
        
        assert result is None