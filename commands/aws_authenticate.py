import click

from lizzy.aws import get_aws_credentials, get_config_accounts
from lizzy.cli import BaseCommand


class AWSAuthenticateCommand(BaseCommand):
    """Authenticate AWS CLI with the provided credentials."""

    @staticmethod
    def register(command_group):
        @command_group.command()
        def aws_authenticate():
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
