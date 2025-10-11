import click

from lizzy.aws import run_aws_fargate_restart
from lizzy.cli import BaseCommand


class AWSFargateRestartCommand(BaseCommand):
    """Restart an AWS Fargate task of a cluster."""

    @staticmethod
    def register(command_group):
        @command_group.command()
        def aws_fargate_restart_all():
            """Restart an AWS Fargate task of a cluster."""
            click.echo("Restarting AWS Fargate task.")
            run_aws_fargate_restart(all_services=True)
