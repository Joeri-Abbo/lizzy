from lizzy.cli import BaseCommand
from lizzy.aws import get_aws_credentials, get_aws_accounts
import click


class AWSAuthenticateWebhookCommand(BaseCommand):
    """Authenticate AWS CLI with the provided credentials."""

    @staticmethod
    def register(command_group):
        @command_group.command()
        def aws_authenticate():
            """Authenticate AWS CLI with the provided credentials."""
            click.echo("Authenticating AWS CLI.")
            accounts = get_aws_accounts()
            labels = ""
            for account in accounts:
                labels += f"{account['id']} | {account['name']}\n"
            account_name = click.prompt(
                f"Select an AWS account to authenticate \n\n{labels}\n",
                type=click.Choice([str(f"{account['name']}") for account in accounts]),
                show_choices=True,
            )

            (
                aws_access_key_id,
                aws_secret_access_key,
                aws_session_token,
                role_arn,
                profile_name,
            ) = get_aws_credentials(account_name)
            # Set as environment variables
            click.echo("Setting AWS CLI environment variables:")

            click.echo(f'export AWS_ACCESS_KEY_ID="{aws_access_key_id}"')
            click.echo(f'export AWS_SECRET_ACCESS_KEY="{aws_secret_access_key}"')
            click.echo(f'export AWS_SESSION_TOKEN="{aws_session_token}"')
            click.echo(f'export AWS_ROLE_ARN="{role_arn}"')
            click.echo("AWS CLI has been authenticated.")
