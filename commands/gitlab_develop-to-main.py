from lizzy.cli import BaseCommand
from lizzy.gitlab import develop_to_main 
import click

class GitlabDevelopToMainCommand(BaseCommand):
    """Command to create a config file if it does not exist, or open it in vim if it does."""

    @staticmethod
    def register(command_group):
        @command_group.command()
        def gitlab_develop_to_main():
            """Create merge requests to switch from develop to main branch."""
            develop_to_main()
            click.echo("Switched GitLab branches from develop to main.")