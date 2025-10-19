import click

from lizzy.cli import BaseCommand


class DatadogCommands(BaseCommand):
    """Manage Datadog operations."""

    @staticmethod
    def register(command_group):
        @command_group.group()
        def datadog():
            """Manage Datadog operations: bump-components, bump-components-latest, fetch-versions, fetch-version-latest"""
            pass

        @datadog.command(name="bump-components")
        @click.option("--version", prompt=True, help="Datadog version to bump to")
        def bump_components(version):
            """Bump Datadog components to a specific version."""
            DatadogCommands._bump_components(version)

        @datadog.command(name="bump-components-latest")
        def bump_components_latest():
            """Bump Datadog components to the latest version."""
            DatadogCommands._bump_components_latest()

        @datadog.command(name="fetch-versions")
        def fetch_versions():
            """Fetch available Datadog versions."""
            DatadogCommands._fetch_versions()

        @datadog.command(name="fetch-version-latest")
        def fetch_version_latest():
            """Fetch Datadog latest version."""
            DatadogCommands._fetch_version_latest()

        # Register individual commands that show in main help with space syntax
        @command_group.command(name="datadog bump-components")
        @click.option("--version", prompt=True, help="Datadog version to bump to")
        def datadog_bump_components_main(version):
            """Bump Datadog components to a specific version."""
            DatadogCommands._bump_components(version)

        @command_group.command(name="datadog bump-components-latest")
        def datadog_bump_components_latest_main():
            """Bump Datadog components to the latest version."""
            DatadogCommands._bump_components_latest()

        @command_group.command(name="datadog fetch-versions")
        def datadog_fetch_versions_main():
            """Fetch available Datadog versions."""
            DatadogCommands._fetch_versions()

        @command_group.command(name="datadog fetch-version-latest")
        def datadog_fetch_version_latest_main():
            """Fetch Datadog latest version."""
            DatadogCommands._fetch_version_latest()

    @staticmethod
    def _bump_components(version):
        """Bump Datadog components to a specific version."""
        from lizzy.helpers.datadog import get_fetch_versions, bump_datadog_components

        click.echo("Bumping Datadog components...")

        if click.confirm(f"Do you want to check if version {version} exists?"):
            versions = get_fetch_versions()
            if version not in versions:
                click.echo(f"Version {version} not found in available versions.")
                return
            else:
                click.echo(f"Version {version} found. Proceeding with bump.")

        bump_datadog_components(version)
        click.echo(f"Datadog components bumped to version {version}.")

    @staticmethod
    def _bump_components_latest():
        """Bump Datadog components to the latest version."""
        from lizzy.helpers.datadog import get_highest_version, bump_datadog_components

        click.echo("Bumping Datadog components...")
        version = get_highest_version()
        bump_datadog_components(version)
        click.echo(f"Datadog components bumped to version {version}.")

    @staticmethod
    def _fetch_versions():
        """Fetch available Datadog versions."""
        from lizzy.helpers.datadog import get_fetch_versions

        click.echo("Fetching Datadog versions...")
        for tag in sorted(get_fetch_versions()):
            click.echo(f"Datadog Agent: {tag}")

    @staticmethod
    def _fetch_version_latest():
        """Fetch Datadog latest version."""
        from lizzy.helpers.datadog import get_highest_version

        click.echo("Fetching Datadog latest version...")
        click.echo(f"Latest Datadog Agent: {get_highest_version()}")
