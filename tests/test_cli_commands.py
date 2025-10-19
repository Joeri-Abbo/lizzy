"""Tests for CLI commands."""

from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from lizzy.cli import lizzy


class TestCLICommands:
    """Test CLI command functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_main_help_shows_all_command_groups(self):
        """Test that the main help shows all command groups."""
        result = self.runner.invoke(lizzy, ['--help'])
        
        assert result.exit_code == 0
        # Check that all command groups are visible
        assert "aws" in result.output
        assert "chef" in result.output
        assert "datadog" in result.output
        assert "gitlab" in result.output
        assert "terraform" in result.output
        assert "workflows" in result.output
        assert "self" in result.output

    def test_main_help_shows_individual_commands(self):
        """Test that the main help shows individual commands with space syntax."""
        result = self.runner.invoke(lizzy, ['--help'])
        
        assert result.exit_code == 0
        # Check that individual commands are visible
        assert "aws authenticate" in result.output
        assert "datadog fetch-versions" in result.output
        assert "gitlab develop-to-main" in result.output
        assert "self config" in result.output
        assert "workflows create" in result.output

    def test_group_help_shows_subcommands(self):
        """Test that group help shows available subcommands."""
        result = self.runner.invoke(lizzy, ['aws', '--help'])
        
        assert result.exit_code == 0
        assert "authenticate" in result.output
        assert "fargate-restart" in result.output
        assert "fargate-restart-all" in result.output

    def test_invalid_command_shows_error(self):
        """Test that invalid commands show proper error."""
        result = self.runner.invoke(lizzy, ['invalid-command'])
        
        assert result.exit_code != 0
        assert "No such command" in result.output


class TestAWSCommands:
    """Test AWS CLI commands."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    @patch('commands.aws_commands.get_aws_credentials')
    @patch('commands.aws_commands.get_config_accounts')
    def test_aws_authenticate_command(self, mock_get_accounts, mock_get_creds):
        """Test AWS authenticate command."""
        mock_get_accounts.return_value = "dev"
        mock_get_creds.return_value = (
            "test_access_key",
            "test_secret_key", 
            "test_session_token",
            "test_role_arn"
        )

        result = self.runner.invoke(lizzy, ['aws', 'authenticate'])
        
        assert result.exit_code == 0
        assert "AWS_ACCESS_KEY_ID" in result.output
        assert "AWS_SECRET_ACCESS_KEY" in result.output
        assert "AWS_SESSION_TOKEN" in result.output

    @patch('commands.aws_commands.run_aws_fargate_restart')
    def test_aws_fargate_restart_command(self, mock_restart):
        """Test AWS Fargate restart command."""
        result = self.runner.invoke(lizzy, ['aws', 'fargate-restart'])
        
        assert result.exit_code == 0
        mock_restart.assert_called_once_with(all_services=False)

    @patch('commands.aws_commands.run_aws_fargate_restart')
    def test_aws_fargate_restart_all_command(self, mock_restart):
        """Test AWS Fargate restart all command."""
        result = self.runner.invoke(lizzy, ['aws', 'fargate-restart-all'])
        
        assert result.exit_code == 0
        mock_restart.assert_called_once_with(all_services=True)

    def test_aws_group_help(self):
        """Test AWS group help displays correctly."""
        result = self.runner.invoke(lizzy, ['aws', '--help'])
        
        assert result.exit_code == 0
        assert "Manage AWS operations" in result.output


class TestDatadogCommands:
    """Test Datadog CLI commands."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    @patch('commands.datadog_commands.get_fetch_versions')
    def test_datadog_fetch_versions_command(self, mock_get_versions):
        """Test Datadog fetch versions command."""
        mock_get_versions.return_value = ["7.50.0", "7.51.0"]

        result = self.runner.invoke(lizzy, ['datadog', 'fetch-versions'])
        
        assert result.exit_code == 0
        assert "Datadog Agent: 7.50.0" in result.output
        assert "Datadog Agent: 7.51.0" in result.output

    @patch('commands.datadog_commands.get_highest_version')
    def test_datadog_fetch_version_latest_command(self, mock_get_highest):
        """Test Datadog fetch latest version command."""
        mock_get_highest.return_value = "7.51.0"

        result = self.runner.invoke(lizzy, ['datadog', 'fetch-version-latest'])
        
        assert result.exit_code == 0
        assert "Latest Datadog Agent: 7.51.0" in result.output

    @patch('commands.datadog_commands.get_highest_version')
    @patch('commands.datadog_commands.bump_datadog_components')
    def test_datadog_bump_components_latest_command(self, mock_bump, mock_get_highest):
        """Test Datadog bump components latest command."""
        mock_get_highest.return_value = "7.51.0"

        result = self.runner.invoke(lizzy, ['datadog', 'bump-components-latest'])
        
        assert result.exit_code == 0
        mock_bump.assert_called_once_with("7.51.0")

    @patch('commands.datadog_commands.bump_datadog_components')
    @patch('commands.datadog_commands.get_fetch_versions')
    def test_datadog_bump_components_with_version(self, mock_get_versions, mock_bump):
        """Test Datadog bump components with specific version."""
        mock_get_versions.return_value = ["7.50.0", "7.51.0"]

        result = self.runner.invoke(
            lizzy, 
            ['datadog', 'bump-components', '--version', '7.50.0'],
            input='y\n'  # Confirm version check
        )
        
        assert result.exit_code == 0
        mock_bump.assert_called_once_with("7.50.0")


class TestGitlabCommands:
    """Test GitLab CLI commands."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    @patch('commands.gitlab_commands.develop_to_main')
    def test_gitlab_develop_to_main_command(self, mock_develop_to_main):
        """Test GitLab develop to main command."""
        result = self.runner.invoke(lizzy, ['gitlab', 'develop-to-main'])
        
        assert result.exit_code == 0
        mock_develop_to_main.assert_called_once()

    @patch('commands.gitlab_commands.main_to_develop')
    def test_gitlab_main_to_develop_command(self, mock_main_to_develop):
        """Test GitLab main to develop command."""
        result = self.runner.invoke(lizzy, ['gitlab', 'main-to-develop'])
        
        assert result.exit_code == 0
        mock_main_to_develop.assert_called_once()

    @patch('commands.gitlab_commands.fetch_approved_merge_requests')
    def test_gitlab_merge_approved_command(self, mock_fetch_approved):
        """Test GitLab merge approved command."""
        result = self.runner.invoke(lizzy, ['gitlab', 'merge-approved'])
        
        assert result.exit_code == 0
        mock_fetch_approved.assert_called_once()

    @patch('commands.gitlab_commands.remove_merged_branches')
    def test_gitlab_remove_merged_branches_command(self, mock_remove_branches):
        """Test GitLab remove merged branches command."""
        result = self.runner.invoke(lizzy, ['gitlab', 'remove-merged-branches'])
        
        assert result.exit_code == 0
        mock_remove_branches.assert_called_once()


class TestTerraformCommands:
    """Test Terraform CLI commands."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    @patch('commands.terraform_commands.discard_plans')
    def test_terraform_discard_plans_command(self, mock_discard_plans):
        """Test Terraform discard plans command."""
        result = self.runner.invoke(lizzy, ['terraform', 'discard-plans'])
        
        assert result.exit_code == 0
        mock_discard_plans.assert_called_once()

    @patch('commands.terraform_commands.set_slack_webhook')
    def test_terraform_set_slack_webhook_command(self, mock_set_webhook):
        """Test Terraform set Slack webhook command."""
        result = self.runner.invoke(lizzy, ['terraform', 'set-slack-webhook'])
        
        assert result.exit_code == 0
        mock_set_webhook.assert_called_once()


class TestChefCommands:
    """Test Chef CLI commands."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    @patch('commands.chef_commands.update_chef_version')
    def test_chef_modify_chef_version_command(self, mock_update_chef):
        """Test Chef modify chef version command."""
        result = self.runner.invoke(lizzy, ['chef', 'modify-chef-version'])
        
        assert result.exit_code == 0
        mock_update_chef.assert_called_once()

    @patch('commands.chef_commands.update_datadog_version')
    def test_chef_modify_datadog_version_command(self, mock_update_datadog):
        """Test Chef modify datadog version command."""
        result = self.runner.invoke(lizzy, ['chef', 'modify-datadog-version'])
        
        assert result.exit_code == 0
        mock_update_datadog.assert_called_once()


class TestSelfCommands:
    """Test Self CLI commands."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    @patch('commands.self_commands.edit_lizzy_config')
    def test_self_config_command(self, mock_edit_config):
        """Test self config command."""
        result = self.runner.invoke(lizzy, ['self', 'config'])
        
        assert result.exit_code == 0
        mock_edit_config.assert_called_once()

    @patch('commands.self_commands.subprocess.run')
    @patch('commands.self_commands.tempfile.TemporaryDirectory')
    def test_self_update_command(self, mock_temp_dir, mock_subprocess_run):
        """Test self update command."""
        mock_temp_dir.return_value.__enter__.return_value = "/tmp/test"
        mock_subprocess_run.return_value = MagicMock()

        result = self.runner.invoke(lizzy, ['self', 'update'])
        
        assert result.exit_code == 0
        assert mock_subprocess_run.call_count >= 2  # At least git clone and pip install


class TestWorkflowsCommands:
    """Test Workflows CLI commands."""

    def setup_method(self):
        """Set up test fixtures.""" 
        self.runner = CliRunner()

    @patch('commands.workflows.os.makedirs')
    @patch('commands.workflows.os.path.exists')
    @patch('builtins.open', create=True)
    def test_workflows_create_command(self, mock_open, mock_exists, mock_makedirs):
        """Test workflows create command."""
        mock_exists.return_value = False
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        result = self.runner.invoke(
            lizzy, 
            ['workflows', 'create'],
            input='test-workflow\nTest description\n'
        )
        
        assert result.exit_code == 0
        assert "Workflow 'test-workflow' created successfully" in result.output

    @patch('commands.workflows.os.path.exists')
    @patch('commands.workflows.os.listdir')
    def test_workflows_list_empty_command(self, mock_listdir, mock_exists):
        """Test workflows list command when no workflows exist."""
        mock_exists.return_value = True
        mock_listdir.return_value = []

        result = self.runner.invoke(lizzy, ['workflows', 'list'])
        
        assert result.exit_code == 0
        assert "No workflows found" in result.output

    @patch('commands.workflows.os.path.exists')
    def test_workflows_list_no_directory_command(self, mock_exists):
        """Test workflows list command when directory doesn't exist."""
        mock_exists.return_value = False

        result = self.runner.invoke(lizzy, ['workflows', 'list'])
        
        assert result.exit_code == 0
        assert "No workflows directory found" in result.output


class TestSpaceSyntaxCommands:
    """Test that space syntax commands work correctly."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    @patch('commands.aws_commands.get_aws_credentials')
    @patch('commands.aws_commands.get_config_accounts')
    def test_space_syntax_aws_authenticate(self, mock_get_accounts, mock_get_creds):
        """Test that space syntax works for AWS authenticate."""
        mock_get_accounts.return_value = "dev"
        mock_get_creds.return_value = ("key", "secret", "token", "arn")

        result = self.runner.invoke(lizzy, ['aws authenticate'])
        
        assert result.exit_code == 0
        assert "AWS_ACCESS_KEY_ID" in result.output

    @patch('commands.datadog_commands.get_fetch_versions')
    def test_space_syntax_datadog_fetch_versions(self, mock_get_versions):
        """Test that space syntax works for Datadog fetch versions."""
        mock_get_versions.return_value = ["7.50.0"]

        result = self.runner.invoke(lizzy, ['datadog fetch-versions'])
        
        assert result.exit_code == 0
        assert "Datadog Agent: 7.50.0" in result.output

    @patch('commands.self_commands.edit_lizzy_config')
    def test_space_syntax_self_config(self, mock_edit_config):
        """Test that space syntax works for self config."""
        result = self.runner.invoke(lizzy, ['self config'])
        
        assert result.exit_code == 0
        mock_edit_config.assert_called_once()