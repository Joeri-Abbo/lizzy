import click

from lizzy.cli import BaseCommand


class SelfCommands(BaseCommand):
    """Manage self operations."""

    @staticmethod
    def register(command_group):
        @command_group.group()
        def self():
            """Manage self operations: config, update"""
            pass

        @self.command()
        def config():
            """Create or open the config file in ~/.lizzy/config.json using vim."""
            SelfCommands._config()

        @self.command()
        def update():
            """Update the Lizzy CLI itself."""
            SelfCommands._update()

        # Register individual commands that show in main help with space syntax
        @command_group.command(name="self config")
        def self_config_main():
            """Create or open the config file in ~/.lizzy/config.json using vim."""
            SelfCommands._config()

        @command_group.command(name="self update")
        def self_update_main():
            """Update the Lizzy CLI itself."""
            SelfCommands._update()

    @staticmethod
    def _config():
        """Create or open the config file in ~/.lizzy/config.json using vim."""
        from lizzy.helpers.config import edit_config as edit_lizzy_config
        edit_lizzy_config()
        click.echo("Config updated/opened successfully.")

    @staticmethod
    def _update():
        """Update the Lizzy CLI itself."""
        import subprocess
        import tempfile
        import sys
        from pathlib import Path
        
        repo_url = "git@github.com:Joeri-Abbo/lizzy.git"
        branch = "master"

        click.echo(f"🔄 Updating Lizzy CLI from {repo_url}...")

        # Create a temporary directory for cloning
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                # Clone the repository
                click.echo("📦 Cloning repository to temporary directory...")
                subprocess.run(
                    [
                        "git",
                        "clone",
                        "--branch",
                        branch,
                        "--depth",
                        "1",
                        repo_url,
                        temp_dir,
                    ],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                click.echo("✅ Repository cloned successfully")

                # Navigate to the cloned directory and install
                setup_py_path = Path(temp_dir) / "setup.py"

                if not setup_py_path.exists():
                    click.echo(
                        "❌ Error: setup.py not found in the repository", err=True
                    )
                    sys.exit(1)

                click.echo("📥 Installing updated packages...")

                # Install the package in editable mode with pip
                # Use sys.executable to ensure we use the correct Python interpreter
                subprocess.run(
                    [
                        sys.executable,
                        "-m",
                        "pip",
                        "install",
                        "--upgrade",
                        "-e",
                        temp_dir,
                    ],
                    capture_output=True,
                    text=True,
                    check=True,
                )

                click.echo("✅ Lizzy CLI has been successfully updated!")
                click.echo(
                    "ℹ️  Please restart your terminal or run 'lizzy' to use the updated version."
                )

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