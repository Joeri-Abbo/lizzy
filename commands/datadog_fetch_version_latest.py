import click
from lizzy.cli import BaseCommand
from lizzy.datadog import get_fetch_versions


class DatadogVersionLatestCommand(BaseCommand):
    """Command to fetch Datadog latest version."""
    @staticmethod
    def register(command_group):
        @command_group.command()
        def fetch_datadog_version_latest():
            """Fetch Datadog latest version."""
            click.echo("Fetching Datadog latest version...")
            versions = get_fetch_versions()
            click.echo(f"Latest Datadog Agent: {max(versions, key=lambda v: list(map(int, v.split('.'))))}")