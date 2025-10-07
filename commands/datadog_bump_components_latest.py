import click
from lizzy.cli import BaseCommand
from lizzy.datadog import get_highest_version, bump_datadog_components


class DatadogBumpComponentsLatestCommand(BaseCommand):
    """Command to fetch Datadog latest version."""

    @staticmethod
    def register(command_group):
        @command_group.command()
        def bump_datadog_components_latest():
            """Bump Datadog components to the latest version."""
            click.echo("Bumping Datadog components...")
            version = get_highest_version()
            bump_datadog_components(version)
            click.echo(f"Datadog components bumped to version {version}.")
