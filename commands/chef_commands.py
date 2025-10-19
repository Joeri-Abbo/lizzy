import click

from lizzy.cli import BaseCommand


class ChefCommands(BaseCommand):
    """Manage Chef operations."""

    @staticmethod
    def register(command_group):
        @command_group.group()
        def chef():
            """Manage Chef operations: modify-chef-version, modify-datadog-version"""
            pass

        @chef.command(name="modify-chef-version")
        def modify_chef_version():
            """Modify the Chef version in Chef configurations."""
            ChefCommands._modify_chef_version()

        @chef.command(name="modify-datadog-version")
        def modify_datadog_version():
            """Modify the Datadog version in Chef configurations."""
            ChefCommands._modify_datadog_version()

        # Register individual commands that show in main help with space syntax
        @command_group.command(name="chef modify-chef-version")
        def chef_modify_chef_version_main():
            """Modify the Chef version in Chef configurations."""
            ChefCommands._modify_chef_version()

        @command_group.command(name="chef modify-datadog-version")
        def chef_modify_datadog_version_main():
            """Modify the Datadog version in Chef configurations."""
            ChefCommands._modify_datadog_version()

    @staticmethod
    def _modify_chef_version():
        """Modify the Chef version in Chef configurations."""
        from lizzy.helpers.chef import update_chef_version
        click.echo("Modifying Chef version in Chef configurations.")
        update_chef_version()
        click.echo("Chef version has been updated successfully.")

    @staticmethod
    def _modify_datadog_version():
        """Modify the Datadog version in Chef configurations."""
        from lizzy.helpers.chef import update_datadog_version
        click.echo("Modifying Datadog version in Chef configurations.")
        update_datadog_version()
        click.echo("Datadog version in Chef has been updated successfully.")