import click

from lizzy.chef import update_datadog_version
from lizzy.cli import BaseCommand


class ChefModifyDatadogVersionCommand(BaseCommand):
    """Modify the Datadog version in Chef configurations."""

    @staticmethod
    def register(command_group):
        @command_group.command()
        def chef_modify_datadog_version():
            """Modify the Datadog version in Chef configurations."""
            click.echo("Modifying Datadog version in Chef configurations.")
            update_datadog_version()
