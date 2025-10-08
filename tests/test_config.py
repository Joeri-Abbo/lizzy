"""Tests for lizzy.config module."""

from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

from lizzy.config import (
    config_dir,
    config_path,
    edit_config,
    example_config_path,
    get_config,
    get_setting,
)


class TestConfigPaths:
    """Test configuration path functions."""

    def test_config_dir_returns_path_in_home(self):
        """Test that config_dir returns a path in the home directory."""
        result = config_dir()
        assert isinstance(result, Path)
        assert ".lizzy" in str(result)
        assert str(Path.home()) in str(result)

    def test_config_path_returns_config_json(self):
        """Test that config_path returns the config.json file path."""
        result = config_path()
        assert isinstance(result, Path)
        assert str(result).endswith("config.json")

    def test_example_config_path_returns_example_config(self):
        """Test that example_config_path returns the example config file path."""
        result = example_config_path()
        assert isinstance(result, Path)
        assert str(result).endswith("example_config.json")


class TestGetConfig:
    """Test get_config function."""

    @patch("lizzy.config.config_path")
    @patch("builtins.open", new_callable=mock_open, read_data='{"test": "value"}')
    def test_get_config_loads_existing_config(self, mock_file, mock_config_path):
        """Test that get_config loads an existing config file."""
        mock_path = MagicMock()
        mock_path.exists.return_value = True
        mock_config_path.return_value = mock_path

        result = get_config()

        assert result == {"test": "value"}
        mock_file.assert_called_once()

    @patch("lizzy.config.config_path")
    @patch("lizzy.config.example_config_path")
    @patch("builtins.open", new_callable=mock_open, read_data='{"example": "config"}')
    def test_get_config_loads_example_when_config_missing(
        self, mock_file, mock_example_path, mock_config_path
    ):
        """Test that get_config loads example config when config file doesn't exist."""
        mock_path = MagicMock()
        mock_path.exists.return_value = False
        mock_config_path.return_value = mock_path
        mock_example_path.return_value = Path("/fake/example_config.json")

        result = get_config()

        assert result == {"example": "config"}


class TestEditConfig:
    """Test edit_config function."""

    @patch("lizzy.config.config_path")
    @patch("lizzy.config.config_dir")
    @patch("lizzy.config.example_config_path")
    @patch("subprocess.run")
    @patch("builtins.open", new_callable=mock_open, read_data='{"example": "config"}')
    @patch("click.echo")
    def test_edit_config_creates_new_config_if_missing(
        self,
        mock_echo,
        mock_file,
        mock_subprocess,
        mock_example_path,
        mock_config_dir_func,
        mock_config_path_func,
    ):
        """Test that edit_config creates a new config file if it doesn't exist."""
        mock_path = MagicMock()
        mock_path.exists.return_value = False
        mock_config_path_func.return_value = mock_path

        mock_dir = MagicMock()
        mock_dir.mkdir = MagicMock()
        mock_config_dir_func.return_value = mock_dir

        mock_example_path.return_value = Path("/fake/example_config.json")

        edit_config()

        mock_dir.mkdir.assert_called_once_with(parents=True, exist_ok=True)
        mock_subprocess.assert_called_once()
        assert "vim" in str(mock_subprocess.call_args)

    @patch("lizzy.config.config_path")
    @patch("subprocess.run")
    def test_edit_config_opens_existing_config(
        self, mock_subprocess, mock_config_path_func
    ):
        """Test that edit_config opens an existing config file."""
        mock_path = MagicMock()
        mock_path.exists.return_value = True
        mock_config_path_func.return_value = mock_path

        edit_config()

        mock_subprocess.assert_called_once()
        assert "vim" in str(mock_subprocess.call_args)

    @patch("lizzy.config.config_path")
    @patch("subprocess.run", side_effect=FileNotFoundError)
    @patch("click.echo")
    def test_edit_config_handles_missing_vim(
        self, mock_echo, mock_subprocess, mock_config_path_func
    ):
        """Test that edit_config handles missing vim gracefully."""
        mock_path = MagicMock()
        mock_path.exists.return_value = True
        mock_config_path_func.return_value = mock_path

        edit_config()

        mock_echo.assert_called()
        assert any(
            "vim is not installed" in str(call) for call in mock_echo.call_args_list
        )


class TestGetSetting:
    """Test get_setting function."""

    @patch("lizzy.config.get_config")
    def test_get_setting_returns_nested_value(self, mock_get_config):
        """Test that get_setting retrieves nested configuration values."""
        mock_get_config.return_value = {
            "gitlab": {"api_token": "test_token", "username": "test_user"},
            "aws": {"accounts": [{"name": "dev", "id": "123"}]},
        }

        result = get_setting("gitlab.api_token")
        assert result == "test_token"

        result = get_setting("aws.accounts")
        assert result == [{"name": "dev", "id": "123"}]

    @patch("lizzy.config.get_config")
    def test_get_setting_returns_none_for_missing_key(self, mock_get_config):
        """Test that get_setting returns None for missing keys."""
        mock_get_config.return_value = {"gitlab": {"api_token": "test_token"}}

        result = get_setting("nonexistent.key")
        assert result is None

    @patch("lizzy.config.get_config")
    def test_get_setting_returns_none_for_empty_setting(self, mock_get_config):
        """Test that get_setting returns None for empty setting string."""
        mock_get_config.return_value = {"test": "value"}

        result = get_setting("")
        assert result is None

        result = get_setting(None)
        assert result is None

    @patch("lizzy.config.get_config")
    def test_get_setting_handles_partial_path(self, mock_get_config):
        """Test that get_setting handles partial paths correctly."""
        mock_get_config.return_value = {
            "gitlab": {"api_token": "test_token", "username": "test_user"}
        }

        result = get_setting("gitlab")
        assert result == {"api_token": "test_token", "username": "test_user"}
