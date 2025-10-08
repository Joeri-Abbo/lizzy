import click

from lizzy.cli import BaseCommand
from lizzy.config import edit_config as edit_lizzy_config


class EditConfigCommand(BaseCommand):
    """Command to create a config file if it does not exist, or open it in vim if it does."""

    @staticmethod
    def register(command_group):
        @command_group.command()
        def edit_config():
            """Create or open the config file in ~/.lizzy/config.json using vim."""
            edit_lizzy_config()
            click.echo("Config updated/opened successfully.")
