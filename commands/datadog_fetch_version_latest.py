import click

from lizzy.cli import BaseCommand
from lizzy.datadog import get_highest_version


class DatadogVersionLatestCommand(BaseCommand):
    """Command to fetch Datadog latest version."""

    @staticmethod
    def register(command_group):
        @command_group.command()
        def fetch_datadog_version_latest():
            """Fetch Datadog latest version."""
            click.echo("Fetching Datadog latest version...")
            click.echo(f"Latest Datadog Agent: {get_highest_version()}")
