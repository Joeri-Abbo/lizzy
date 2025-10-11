import click

from lizzy.chef import update_chef_version
from lizzy.cli import BaseCommand


class ChefModifyChefVersionCommand(BaseCommand):
    """Modify the Chef version in Chef configurations."""

    @staticmethod
    def register(command_group):
        @command_group.command()
        def chef_modify_chef_version():
            """Modify the Chef version in Chef configurations."""
            click.echo("Modifying Chef version in Chef configurations.")
            update_chef_version()
