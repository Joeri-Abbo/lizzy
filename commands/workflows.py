import click
import os
import json
from datetime import datetime

from lizzy.cli import BaseCommand

# Constants
WORKFLOWS_DIR = "~/.lizzy/workflows"
JSON_EXT = ".json"


class WorkflowsCommand(BaseCommand):
    """Manage workflows for the project."""

    @staticmethod
    def register(command_group):
        @command_group.group()
        def workflows():
            """Manage workflows: create, run, list"""
            pass

        @workflows.command()
        def create():
            """Create a new workflow."""
            WorkflowsCommand._create_workflow()

        @workflows.command()
        @click.argument('workflow_name', required=False)
        def run(workflow_name):
            """Run a workflow by name."""
            WorkflowsCommand._run_workflow(workflow_name)

        @workflows.command()
        def list():
            """List all available workflows."""
            WorkflowsCommand._list_workflows()

        # Register individual commands that show in main help with space syntax
        @command_group.command(name="workflows create")
        def workflows_create_main():
            """Create a new workflow."""
            WorkflowsCommand._create_workflow()

        @command_group.command(name="workflows run")
        @click.argument('workflow_name', required=False)
        def workflows_run_main(workflow_name):
            """Run a workflow by name."""
            WorkflowsCommand._run_workflow(workflow_name)

        @command_group.command(name="workflows list")
        def workflows_list_main():
            """List all available workflows."""
            WorkflowsCommand._list_workflows()

    @staticmethod
    def _get_workflows_dir():
        """Get the workflows directory path."""
        return os.path.expanduser(WORKFLOWS_DIR)

    @staticmethod
    def _create_workflow():
        """Create a new workflow."""
        workflow_name = click.prompt("Workflow name")
        workflow_description = click.prompt("Workflow description")
        
        workflows_dir = WorkflowsCommand._get_workflows_dir()
        os.makedirs(workflows_dir, exist_ok=True)
        
        workflow_config = {
            "name": workflow_name,
            "description": workflow_description,
            "created_at": datetime.now().isoformat(),
            "steps": [
                {
                    "name": "example_step",
                    "command": "echo 'Hello from workflow'",
                    "description": "Example step - replace with your commands"
                }
            ]
        }
        
        workflow_file = os.path.join(workflows_dir, f"{workflow_name}{JSON_EXT}")
        
        if os.path.exists(workflow_file):
            if not click.confirm(f"Workflow '{workflow_name}' already exists. Overwrite?"):
                click.echo("Workflow creation cancelled.")
                return
        
        with open(workflow_file, 'w') as f:
            json.dump(workflow_config, f, indent=2)
        
        click.echo(f"✅ Workflow '{workflow_name}' created successfully at {workflow_file}")
        click.echo("💡 Edit the workflow file to customize the steps.")

    @staticmethod
    def _get_available_workflows(workflows_dir):
        """Get list of available workflow names."""
        return [f.replace(JSON_EXT, '') for f in os.listdir(workflows_dir) if f.endswith(JSON_EXT)]

    @staticmethod
    def _select_workflow_interactively(workflows):
        """Allow user to select a workflow from available options."""
        click.echo("Available workflows:")
        for i, wf in enumerate(workflows, 1):
            click.echo(f"  {i}. {wf}")
        
        choice = click.prompt("Select workflow number", type=int)
        if 1 <= choice <= len(workflows):
            return workflows[choice - 1]
        else:
            click.echo("❌ Invalid selection.")
            return None

    @staticmethod
    def _execute_workflow_step(step, step_number):
        """Execute a single workflow step."""
        click.echo(f"📋 Step {step_number}: {step['name']}")
        if 'description' in step:
            click.echo(f"   Description: {step['description']}")
        
        command = step.get('command', '')
        if command:
            click.echo(f"   Command: {command}")
            if click.confirm("Execute this step?", default=True):
                result = os.system(command)
                if result == 0:
                    click.echo(f"   ✅ Step {step_number} completed successfully")
                    return True
                else:
                    click.echo(f"   ❌ Step {step_number} failed with exit code {result}")
                    return click.confirm("Continue with next step?")
            else:
                click.echo(f"   ⏭️  Step {step_number} skipped")
                return True
        else:
            click.echo("   ⚠️  No command specified for this step")
            return True

    @staticmethod
    def _run_workflow(workflow_name):
        """Run a workflow by name."""
        workflows_dir = WorkflowsCommand._get_workflows_dir()
        
        if not os.path.exists(workflows_dir):
            click.echo("❌ No workflows directory found. Create a workflow first with 'lizzy workflows create'.")
            return
        
        # If no workflow name provided, list available workflows and prompt
        if not workflow_name:
            workflows = WorkflowsCommand._get_available_workflows(workflows_dir)
            if not workflows:
                click.echo("❌ No workflows found. Create a workflow first with 'lizzy workflows create'.")
                return
            
            workflow_name = WorkflowsCommand._select_workflow_interactively(workflows)
            if not workflow_name:
                return
        
        workflow_file = os.path.join(workflows_dir, f"{workflow_name}{JSON_EXT}")
        
        if not os.path.exists(workflow_file):
            click.echo(f"❌ Workflow '{workflow_name}' not found.")
            return
        
        # Load and run workflow
        with open(workflow_file, 'r') as f:
            workflow_config = json.load(f)
        
        click.echo(f"🚀 Running workflow: {workflow_config['name']}")
        click.echo(f"� Description: {workflow_config['description']}")
        click.echo("=" * 50)
        
        for i, step in enumerate(workflow_config.get('steps', []), 1):
            if not WorkflowsCommand._execute_workflow_step(step, i):
                break
            click.echo("")
        
        click.echo("🏁 Workflow execution completed!")

    @staticmethod
    def _display_workflow_info(workflow_file, workflows_dir):
        """Display information for a single workflow."""
        workflow_path = os.path.join(workflows_dir, workflow_file)
        try:
            with open(workflow_path, 'r') as f:
                workflow_config = json.load(f)
            
            name = workflow_config.get('name', workflow_file.replace(JSON_EXT, ''))
            description = workflow_config.get('description', 'No description')
            created_at = workflow_config.get('created_at', 'Unknown')
            steps_count = len(workflow_config.get('steps', []))
            
            click.echo(f"📄 {name}")
            click.echo(f"   Description: {description}")
            click.echo(f"   Created: {created_at}")
            click.echo(f"   Steps: {steps_count}")
            click.echo(f"   File: {workflow_path}")
            click.echo("")
            
        except (json.JSONDecodeError, KeyError) as e:
            click.echo(f"⚠️  {workflow_file}: Invalid workflow file ({e})")
            click.echo("")

    @staticmethod
    def _list_workflows():
        """List all available workflows."""
        workflows_dir = WorkflowsCommand._get_workflows_dir()
        
        if not os.path.exists(workflows_dir):
            click.echo("❌ No workflows directory found. Create a workflow first with 'lizzy workflows create'.")
            return
        
        workflow_files = [f for f in os.listdir(workflows_dir) if f.endswith(JSON_EXT)]
        
        if not workflow_files:
            click.echo("📭 No workflows found. Create a workflow with 'lizzy workflows create'.")
            return
        
        click.echo("📚 Available workflows:")
        click.echo("=" * 60)
        
        for workflow_file in sorted(workflow_files):
            WorkflowsCommand._display_workflow_info(workflow_file, workflows_dir)