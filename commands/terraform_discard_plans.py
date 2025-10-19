import click

from lizzy.cli import BaseCommand
from lizzy.terraform import discard_plans


class TerraformDiscardPlansCommand(BaseCommand):
    """Command to discard Terraform plans."""

    @staticmethod
    def register(command_group):
        @command_group.command()
        def terraform_discard_plans():
            """Discard Terraform plans."""
            click.echo("Discarding Terraform plans.")
            discard_plans()
            click.echo("Terraform plans have been discarded.")
