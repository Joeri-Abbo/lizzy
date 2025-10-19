import click

from lizzy.helpers.aws import get_aws_credentials, get_config_accounts
from lizzy.cli import BaseCommand


class AWSCommands(BaseCommand):
    """Manage AWS operations."""

    @staticmethod
    def register(command_group):
        @command_group.group()
        def aws():
            """Manage AWS operations: authenticate, fargate-restart, fargate-restart-all"""
            pass

        @aws.command()
        def authenticate():
            """Authenticate AWS CLI with the provided credentials."""
            AWSCommands._authenticate()

        @aws.command(name="fargate-restart")
        def fargate_restart():
            """Restart an AWS Fargate task of a specific service."""
            AWSCommands._fargate_restart()

        @aws.command(name="fargate-restart-all")
        def fargate_restart_all():
            """Restart all AWS Fargate tasks."""
            AWSCommands._fargate_restart_all()

        # Register individual commands that show in main help with space syntax
        @command_group.command(name="aws authenticate")
        def aws_authenticate_main():
            """Authenticate AWS CLI with the provided credentials."""
            AWSCommands._authenticate()

        @command_group.command(name="aws fargate-restart")
        def aws_fargate_restart_main():
            """Restart an AWS Fargate task of a specific service."""
            AWSCommands._fargate_restart()

        @command_group.command(name="aws fargate-restart-all")
        def aws_fargate_restart_all_main():
            """Restart all AWS Fargate tasks."""
            AWSCommands._fargate_restart_all()

    @staticmethod
    def _authenticate():
        """Authenticate AWS CLI with the provided credentials."""
        click.echo("Authenticating AWS CLI.")
        (
            aws_access_key_id,
            aws_secret_access_key,
            aws_session_token,
            role_arn,
        ) = get_aws_credentials(get_config_accounts())
        # Set as environment variables
        click.echo("Setting AWS CLI environment variables:")
        click.echo(f'export AWS_ACCESS_KEY_ID="{aws_access_key_id}"')
        click.echo(f'export AWS_SECRET_ACCESS_KEY="{aws_secret_access_key}"')
        click.echo(f'export AWS_SESSION_TOKEN="{aws_session_token}"')
        click.echo(f'export AWS_ROLE_ARN="{role_arn}"')
        click.echo("AWS CLI has been authenticated.")

    @staticmethod
    def _fargate_restart():
        """Restart an AWS Fargate task of a specific service."""
        from lizzy.helpers.aws import run_aws_fargate_restart

        click.echo("Restarting AWS Fargate task.")
        run_aws_fargate_restart(all_services=False)

    @staticmethod
    def _fargate_restart_all():
        """Restart all AWS Fargate tasks."""
        from lizzy.helpers.aws import run_aws_fargate_restart

        click.echo("Restarting all AWS Fargate tasks...")
        run_aws_fargate_restart(all_services=True)
        click.echo("All AWS Fargate services have been restarted.")
