import click

from lizzy.cli import BaseCommand
from lizzy.datadog import get_fetch_versions


class DatadogVersionsCommand(BaseCommand):
    """Command to fetch Datadog versions."""

    @staticmethod
    def register(command_group):
        @command_group.command()
        def fetch_datadog_versions():
            """Fetch Datadog versions."""
            click.echo("Fetching Datadog versions...")
            for tag in sorted(get_fetch_versions()):
                click.echo(f"Datadog Agent: {tag}")
