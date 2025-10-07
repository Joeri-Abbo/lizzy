from lizzy.cli import BaseCommand
from lizzy.gitlab import remove_merged_branches
import click


class GitlabRemoveMergedBranchesCommand(BaseCommand):
    """Command to remove merged branches in GitLab."""

    @staticmethod
    def register(command_group):
        @command_group.command()
        def gitlab_remove_merged_branches():
            """Remove all merged branches in GitLab."""
            remove_merged_branches()
            click.echo("Removed merged branches from GitLab.")
