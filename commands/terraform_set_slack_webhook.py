import click

from lizzy.cli import BaseCommand
from lizzy.terraform import set_slack_webhook


class TerraformSetSlackWebhookCommand(BaseCommand):
    """Command to set the Slack webhook URL for Terraform."""

    @staticmethod
    def register(command_group):
        @command_group.command()
        def terraform_set_slack_webhook():
            """Set the Slack webhook URL for Terraform."""
            click.echo("Setting Slack webhook URL for Terraform.")
            set_slack_webhook()
            click.echo("Slack webhook URL for Terraform has been set.")
