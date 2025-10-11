import click
import subprocess
import tempfile
import shutil
import os
import sys
from pathlib import Path

from lizzy.cli import BaseCommand


class SelfUpdateCommand(BaseCommand):
    """Command to update the Lizzy CLI itself."""

    @staticmethod
    def register(command_group):
        @command_group.command()
        def self_update():
            """Update the Lizzy CLI itself."""
            repo_url = "git@github.com:Joeri-Abbo/lizzy.git"
            branch = "master"
            
            click.echo(f"🔄 Updating Lizzy CLI from {repo_url}...")
            
            # Create a temporary directory for cloning
            with tempfile.TemporaryDirectory() as temp_dir:
                try:
                    # Clone the repository
                    click.echo(f"📦 Cloning repository to temporary directory...")
                    result = subprocess.run(
                        ["git", "clone", "--branch", branch, "--depth", "1", repo_url, temp_dir],
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    click.echo("✅ Repository cloned successfully")
                    
                    # Navigate to the cloned directory and install
                    setup_py_path = Path(temp_dir) / "setup.py"
                    
                    if not setup_py_path.exists():
                        click.echo("❌ Error: setup.py not found in the repository", err=True)
                        sys.exit(1)
                    
                    click.echo("📥 Installing updated packages...")
                    
                    # Install the package in editable mode with pip
                    # Use sys.executable to ensure we use the correct Python interpreter
                    install_result = subprocess.run(
                        [sys.executable, "-m", "pip", "install", "--upgrade", "-e", temp_dir],
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    
                    click.echo("✅ Lizzy CLI has been successfully updated!")
                    click.echo("ℹ️  Please restart your terminal or run 'lizzy' to use the updated version.")
                    
                except subprocess.CalledProcessError as e:
                    click.echo(f"❌ Error during update: {e}", err=True)
                    if e.stdout:
                        click.echo(f"Output: {e.stdout}", err=True)
                    if e.stderr:
                        click.echo(f"Error: {e.stderr}", err=True)
                    sys.exit(1)
                except Exception as e:
                    click.echo(f"❌ Unexpected error: {str(e)}", err=True)
                    sys.exit(1)