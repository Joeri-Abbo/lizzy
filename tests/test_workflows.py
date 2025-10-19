"""Tests for commands.workflows module."""

import json
import os
import tempfile
from unittest.mock import MagicMock, patch, mock_open, call

import pytest

from commands.workflows import WorkflowsCommand


class TestGetWorkflowsDir:
    """Test _get_workflows_dir method."""

    @patch("commands.workflows.os.path.expanduser")
    def test_get_workflows_dir_expands_user_path(self, mock_expanduser):
        """Test that _get_workflows_dir expands the user path."""
        mock_expanduser.return_value = "/home/user/.lizzy/workflows"
        
        result = WorkflowsCommand._get_workflows_dir()
        
        assert result == "/home/user/.lizzy/workflows"
        mock_expanduser.assert_called_once_with("~/.lizzy/workflows")


class TestCreateWorkflow:
    """Test _create_workflow method."""

    @patch("commands.workflows.WorkflowsCommand._get_workflows_dir")
    @patch("commands.workflows.os.makedirs")
    @patch("commands.workflows.os.path.exists")
    @patch("commands.workflows.click.prompt")
    @patch("commands.workflows.click.echo")
    @patch("builtins.open", new_callable=mock_open)
    @patch("commands.workflows.json.dump")
    @patch("commands.workflows.datetime")
    def test_create_workflow_success(
        self, mock_datetime, mock_json_dump, mock_file, mock_echo, mock_prompt,
        mock_exists, mock_makedirs, mock_get_dir
    ):
        """Test successful workflow creation."""
        mock_get_dir.return_value = "/tmp/workflows"
        mock_exists.return_value = False
        mock_prompt.side_effect = ["test_workflow", "Test workflow description"]
        mock_datetime.now.return_value.isoformat.return_value = "2023-01-01T12:00:00"
        
        WorkflowsCommand._create_workflow()
        
        mock_makedirs.assert_called_once_with("/tmp/workflows", exist_ok=True)
        mock_file.assert_called_once_with("/tmp/workflows/test_workflow.json", 'w')
        
        # Verify the workflow config structure
        call_args = mock_json_dump.call_args[0]
        workflow_config = call_args[0]
        assert workflow_config["name"] == "test_workflow"
        assert workflow_config["description"] == "Test workflow description"
        assert workflow_config["created_at"] == "2023-01-01T12:00:00"
        assert len(workflow_config["steps"]) == 1
        assert workflow_config["steps"][0]["name"] == "example_step"
        
        mock_echo.assert_any_call("✅ Workflow 'test_workflow' created successfully at /tmp/workflows/test_workflow.json")

    @patch("commands.workflows.WorkflowsCommand._get_workflows_dir")
    @patch("commands.workflows.os.makedirs")
    @patch("commands.workflows.os.path.exists")
    @patch("commands.workflows.click.prompt")
    @patch("commands.workflows.click.confirm")
    @patch("commands.workflows.click.echo")
    @patch("builtins.open", new_callable=mock_open)
    @patch("commands.workflows.json.dump")
    def test_create_workflow_overwrite_cancelled(
        self, mock_json_dump, mock_file, mock_echo, mock_confirm, mock_prompt,
        mock_exists, mock_makedirs, mock_get_dir
    ):
        """Test workflow creation cancelled when file exists and overwrite declined."""
        mock_get_dir.return_value = "/tmp/workflows"
        mock_exists.return_value = True
        mock_prompt.side_effect = ["existing_workflow", "Description"]
        mock_confirm.return_value = False
        
        WorkflowsCommand._create_workflow()
        
        mock_confirm.assert_called_once_with("Workflow 'existing_workflow' already exists. Overwrite?")
        mock_echo.assert_any_call("Workflow creation cancelled.")
        mock_json_dump.assert_not_called()

    @patch("commands.workflows.WorkflowsCommand._get_workflows_dir")
    @patch("commands.workflows.os.makedirs")
    @patch("commands.workflows.os.path.exists")
    @patch("commands.workflows.click.prompt")
    @patch("commands.workflows.click.confirm")
    @patch("commands.workflows.click.echo")
    @patch("builtins.open", new_callable=mock_open)
    @patch("commands.workflows.json.dump")
    @patch("commands.workflows.datetime")
    def test_create_workflow_overwrite_confirmed(
        self, mock_datetime, mock_json_dump, mock_file, mock_echo, mock_confirm,
        mock_prompt, mock_exists, mock_makedirs, mock_get_dir
    ):
        """Test workflow creation continues when file exists and overwrite confirmed."""
        mock_get_dir.return_value = "/tmp/workflows"
        mock_exists.return_value = True
        mock_prompt.side_effect = ["existing_workflow", "New description"]
        mock_confirm.return_value = True
        mock_datetime.now.return_value.isoformat.return_value = "2023-01-01T12:00:00"
        
        WorkflowsCommand._create_workflow()
        
        mock_confirm.assert_called_once_with("Workflow 'existing_workflow' already exists. Overwrite?")
        mock_json_dump.assert_called_once()
        mock_echo.assert_any_call("✅ Workflow 'existing_workflow' created successfully at /tmp/workflows/existing_workflow.json")


class TestGetAvailableWorkflows:
    """Test _get_available_workflows method."""

    @patch("commands.workflows.os.listdir")
    def test_get_available_workflows_filters_json_files(self, mock_listdir):
        """Test that _get_available_workflows returns only JSON workflow files."""
        mock_listdir.return_value = [
            "workflow1.json",
            "workflow2.json", 
            "notes.txt",
            "backup.json.bak",
            "workflow3.json"
        ]
        
        result = WorkflowsCommand._get_available_workflows("/tmp/workflows")
        
        assert result == ["workflow1", "workflow2", "workflow3"]

    @patch("commands.workflows.os.listdir")
    def test_get_available_workflows_empty_directory(self, mock_listdir):
        """Test that _get_available_workflows handles empty directory."""
        mock_listdir.return_value = []
        
        result = WorkflowsCommand._get_available_workflows("/tmp/workflows")
        
        assert result == []


class TestSelectWorkflowInteractively:
    """Test _select_workflow_interactively method."""

    @patch("commands.workflows.click.prompt")
    @patch("commands.workflows.click.echo")
    def test_select_workflow_interactively_valid_choice(self, mock_echo, mock_prompt):
        """Test successful workflow selection."""
        workflows = ["workflow1", "workflow2", "workflow3"]
        mock_prompt.return_value = 2
        
        result = WorkflowsCommand._select_workflow_interactively(workflows)
        
        assert result == "workflow2"
        mock_echo.assert_any_call("Available workflows:")
        mock_echo.assert_any_call("  2. workflow2")

    @patch("commands.workflows.click.prompt")
    @patch("commands.workflows.click.echo")
    def test_select_workflow_interactively_invalid_choice(self, mock_echo, mock_prompt):
        """Test invalid workflow selection."""
        workflows = ["workflow1", "workflow2"]
        mock_prompt.return_value = 5  # Invalid choice
        
        result = WorkflowsCommand._select_workflow_interactively(workflows)
        
        assert result is None
        mock_echo.assert_any_call("❌ Invalid selection.")


class TestExecuteWorkflowStep:
    """Test _execute_workflow_step method."""

    @patch("commands.workflows.os.system")
    @patch("commands.workflows.click.confirm")
    @patch("commands.workflows.click.echo")
    def test_execute_workflow_step_success(self, mock_echo, mock_confirm, mock_system):
        """Test successful step execution."""
        step = {
            "name": "test_step",
            "description": "Test step description",
            "command": "echo 'hello'"
        }
        mock_confirm.return_value = True
        mock_system.return_value = 0  # Success exit code
        
        result = WorkflowsCommand._execute_workflow_step(step, 1)
        
        assert result is True
        mock_system.assert_called_once_with("echo 'hello'")
        mock_echo.assert_any_call("📋 Step 1: test_step")
        mock_echo.assert_any_call("   Description: Test step description")
        mock_echo.assert_any_call("   ✅ Step 1 completed successfully")

    @patch("commands.workflows.os.system")
    @patch("commands.workflows.click.confirm")
    @patch("commands.workflows.click.echo")
    def test_execute_workflow_step_skipped(self, mock_echo, mock_confirm, mock_system):
        """Test step execution when skipped."""
        step = {
            "name": "test_step",
            "command": "echo 'hello'"
        }
        mock_confirm.return_value = False  # Don't execute
        
        result = WorkflowsCommand._execute_workflow_step(step, 1)
        
        assert result is True
        mock_system.assert_not_called()
        mock_echo.assert_any_call("   ⏭️  Step 1 skipped")

    @patch("commands.workflows.os.system")
    @patch("commands.workflows.click.confirm")
    @patch("commands.workflows.click.echo")
    def test_execute_workflow_step_failure_continue(self, mock_echo, mock_confirm, mock_system):
        """Test step execution failure with continue choice."""
        step = {
            "name": "test_step",
            "command": "exit 1"
        }
        mock_confirm.side_effect = [True, True]  # Execute step, then continue after failure
        mock_system.return_value = 1  # Failure exit code
        
        result = WorkflowsCommand._execute_workflow_step(step, 1)
        
        assert result is True
        mock_echo.assert_any_call("   ❌ Step 1 failed with exit code 1")

    @patch("commands.workflows.os.system")
    @patch("commands.workflows.click.confirm")
    @patch("commands.workflows.click.echo")
    def test_execute_workflow_step_failure_stop(self, mock_echo, mock_confirm, mock_system):
        """Test step execution failure with stop choice."""
        step = {
            "name": "test_step",
            "command": "exit 1"
        }
        mock_confirm.side_effect = [True, False]  # Execute step, then stop after failure
        mock_system.return_value = 1  # Failure exit code
        
        result = WorkflowsCommand._execute_workflow_step(step, 1)
        
        assert result is False

    @patch("commands.workflows.click.echo")
    def test_execute_workflow_step_no_command(self, mock_echo):
        """Test step execution with no command specified."""
        step = {
            "name": "test_step",
            "description": "Step without command"
        }
        
        result = WorkflowsCommand._execute_workflow_step(step, 1)
        
        assert result is True
        mock_echo.assert_any_call("   ⚠️  No command specified for this step")


class TestRunWorkflow:
    """Test _run_workflow method."""

    @patch("commands.workflows.WorkflowsCommand._get_workflows_dir")
    @patch("commands.workflows.os.path.exists")
    @patch("commands.workflows.click.echo")
    def test_run_workflow_no_workflows_dir(self, mock_echo, mock_exists, mock_get_dir):
        """Test run workflow when workflows directory doesn't exist."""
        mock_get_dir.return_value = "/tmp/workflows"
        mock_exists.return_value = False
        
        WorkflowsCommand._run_workflow("test_workflow")
        
        mock_echo.assert_called_with("❌ No workflows directory found. Create a workflow first with 'lizzy workflows create'.")

    @patch("commands.workflows.WorkflowsCommand._get_workflows_dir")
    @patch("commands.workflows.os.path.exists")
    @patch("commands.workflows.WorkflowsCommand._get_available_workflows")
    @patch("commands.workflows.click.echo")
    def test_run_workflow_no_name_no_workflows(self, mock_echo, mock_get_workflows, mock_exists, mock_get_dir):
        """Test run workflow without name when no workflows exist."""
        mock_get_dir.return_value = "/tmp/workflows"
        mock_exists.return_value = True
        mock_get_workflows.return_value = []
        
        WorkflowsCommand._run_workflow(None)
        
        mock_echo.assert_called_with("❌ No workflows found. Create a workflow first with 'lizzy workflows create'.")

    @patch("commands.workflows.WorkflowsCommand._get_workflows_dir")
    @patch("commands.workflows.os.path.exists")
    @patch("commands.workflows.click.echo")
    def test_run_workflow_not_found(self, mock_echo, mock_exists, mock_get_dir):
        """Test run workflow when specified workflow doesn't exist."""
        mock_get_dir.return_value = "/tmp/workflows"
        mock_exists.side_effect = lambda path: path == "/tmp/workflows"  # Dir exists, file doesn't
        
        WorkflowsCommand._run_workflow("nonexistent")
        
        mock_echo.assert_called_with("❌ Workflow 'nonexistent' not found.")

    @patch("commands.workflows.WorkflowsCommand._get_workflows_dir")
    @patch("commands.workflows.os.path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data='{"name": "test", "description": "Test workflow", "steps": [{"name": "step1", "command": "echo test"}]}')
    @patch("commands.workflows.WorkflowsCommand._execute_workflow_step")
    @patch("commands.workflows.click.echo")
    def test_run_workflow_success(self, mock_echo, mock_execute_step, mock_file, mock_exists, mock_get_dir):
        """Test successful workflow execution."""
        mock_get_dir.return_value = "/tmp/workflows"
        mock_exists.side_effect = lambda path: True  # Both dir and file exist
        mock_execute_step.return_value = True
        
        WorkflowsCommand._run_workflow("test_workflow")
        
        mock_file.assert_called_once_with("/tmp/workflows/test_workflow.json", 'r')
        mock_execute_step.assert_called_once()
        mock_echo.assert_any_call("🚀 Running workflow: test")
        mock_echo.assert_any_call("🏁 Workflow execution completed!")


class TestDisplayWorkflowInfo:
    """Test _display_workflow_info method."""

    @patch("builtins.open", new_callable=mock_open, read_data='{"name": "test_workflow", "description": "Test description", "created_at": "2023-01-01T12:00:00", "steps": [{"name": "step1"}, {"name": "step2"}]}')
    @patch("commands.workflows.click.echo")
    def test_display_workflow_info_success(self, mock_echo, mock_file):
        """Test successful workflow info display."""
        WorkflowsCommand._display_workflow_info("test.json", "/tmp/workflows")
        
        mock_file.assert_called_once_with("/tmp/workflows/test.json", 'r')
        mock_echo.assert_any_call("📄 test_workflow")
        mock_echo.assert_any_call("   Description: Test description")
        mock_echo.assert_any_call("   Created: 2023-01-01T12:00:00")
        mock_echo.assert_any_call("   Steps: 2")

    @patch("builtins.open", new_callable=mock_open, read_data='invalid json')
    @patch("commands.workflows.click.echo")
    def test_display_workflow_info_invalid_json(self, mock_echo, mock_file):
        """Test workflow info display with invalid JSON."""
        WorkflowsCommand._display_workflow_info("invalid.json", "/tmp/workflows")
        
        mock_echo.assert_any_call("⚠️  invalid.json: Invalid workflow file (Expecting value: line 1 column 1 (char 0))")


class TestListWorkflows:
    """Test _list_workflows method."""

    @patch("commands.workflows.WorkflowsCommand._get_workflows_dir")
    @patch("commands.workflows.os.path.exists")
    @patch("commands.workflows.click.echo")
    def test_list_workflows_no_directory(self, mock_echo, mock_exists, mock_get_dir):
        """Test list workflows when directory doesn't exist."""
        mock_get_dir.return_value = "/tmp/workflows"
        mock_exists.return_value = False
        
        WorkflowsCommand._list_workflows()
        
        mock_echo.assert_called_with("❌ No workflows directory found. Create a workflow first with 'lizzy workflows create'.")

    @patch("commands.workflows.WorkflowsCommand._get_workflows_dir")
    @patch("commands.workflows.os.path.exists")
    @patch("commands.workflows.os.listdir")
    @patch("commands.workflows.click.echo")
    def test_list_workflows_empty(self, mock_echo, mock_listdir, mock_exists, mock_get_dir):
        """Test list workflows with no workflows."""
        mock_get_dir.return_value = "/tmp/workflows"
        mock_exists.return_value = True
        mock_listdir.return_value = []
        
        WorkflowsCommand._list_workflows()
        
        mock_echo.assert_called_with("📭 No workflows found. Create a workflow with 'lizzy workflows create'.")

    @patch("commands.workflows.WorkflowsCommand._get_workflows_dir")
    @patch("commands.workflows.os.path.exists")
    @patch("commands.workflows.os.listdir")
    @patch("commands.workflows.WorkflowsCommand._display_workflow_info")
    @patch("commands.workflows.click.echo")
    def test_list_workflows_success(self, mock_echo, mock_display, mock_listdir, mock_exists, mock_get_dir):
        """Test successful workflow listing."""
        mock_get_dir.return_value = "/tmp/workflows"
        mock_exists.return_value = True
        mock_listdir.return_value = ["workflow2.json", "workflow1.json", "notes.txt"]
        
        WorkflowsCommand._list_workflows()
        
        mock_echo.assert_any_call("📚 Available workflows:")
        assert mock_display.call_count == 2
        # Verify workflows are sorted
        mock_display.assert_any_call("workflow1.json", "/tmp/workflows")
        mock_display.assert_any_call("workflow2.json", "/tmp/workflows")