import click

from lizzy.cli import BaseCommand
from lizzy.datadog import get_fetch_versions, bump_datadog_components as bump_datadog_components_now


class DatadogBumpComponentsCommand(BaseCommand):
    """Command to fetch Datadog latest version."""

    @staticmethod
    def register(command_group):
        @command_group.command()
        def bump_datadog_components():
            """Bump Datadog components to the latest version."""
            click.echo("Bumping Datadog components...")
            version = click.prompt("Give me the Datadog version to bump to")
            if input(f"Do you want to check if version {version} exists? (y/n)") == "y":
                versions = get_fetch_versions()
                if version not in versions:
                    click.echo(f"Version {version} not found in available versions.")
                    click.echo("Available versions are:")
                    for v in versions:
                        click.echo(f"- {v}")
                    if input("Do you still want to proceed? (y/n)") != "y":
                        click.echo("Aborting bump operation.")
                        return
            bump_datadog_components_now(version)
            click.echo(f"Datadog components bumped to version {version}.")
