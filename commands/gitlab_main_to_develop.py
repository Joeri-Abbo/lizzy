import click

from lizzy.cli import BaseCommand
from lizzy.gitlab import main_to_develop


class GitlabMainToDevelopCommand(BaseCommand):
    """Command to create a config file if it does not exist, or open it in vim if it does."""

    @staticmethod
    def register(command_group):
        @command_group.command()
        def gitlab_main_to_develop():
            """Create merge requests to switch from main to develop branch."""
            main_to_develop()
            click.echo("Switched GitLab branches from main to develop.")
