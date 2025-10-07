from lizzy.cli import BaseCommand
from lizzy.gitlab import fetch_approved_merge_requests
import click


class GitlabMergeApprovedCommand(BaseCommand):
    """Command to create a config file if it does not exist, or open it in vim if it does."""

    @staticmethod
    def register(command_group):
        @command_group.command()
        def gitlab_merge_approved():
            fetch_approved_merge_requests()
            click.echo("Merged approved pull requests from GitLab.")
