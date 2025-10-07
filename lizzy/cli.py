import click
import importlib
import pkgutil
import inspect
import commands
import sys

ASCII_ART = """
⠀⠀⠀⠀⠀⢀⣠⣤⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⢀⡴⠟⠛⠛⢿⠷⢤⡹⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠸⣧⣀⡀⠈⠻⠷⠀⠇⠙⢦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠘⠪⡛⠦⠄⠀⠀⠀⡄⢈⣻⣦⣄⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠙⢦⠀⠀⢠⠀⣇⣼⣿⡿⢿⣿⣷⣦⣄⠀⠀⠀⣠⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠈⢧⡀⣸⣸⠋⣿⣿⢁⣾⣿⠟⢁⣿⣿⣶⣤⡇⠈⢳⡀⣠⠀⠀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠻⣿⠇⠀⠛⠁⠈⠻⠃⠀⣾⣿⣿⠟⠉⠙⣦⡀⢻⣿⣠⣾⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⡟⠒⢶⣤⡀⠀⠀⠀⠈⠿⣿⠥⣤⡀⢸⣿⣿⣷⣿⣹⣥⣶⠿⠂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⢳⠀⠀⣽⣿⣦⣄⣀⠀⠀⣿⠀⢀⠈⠉⠻⡄⠀⠈⠛⢧⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⢸⡀⠀⡟⠀⠈⠉⠛⠻⢿⡿⠀⠸⣼⡇⠀⠀⠀⣠⠄⢸⣿⡟⠙⠒⢶⣤⣀⣀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠰⠶⣶⠤⣀⣠⡇⠀⡇⠀⠀⠀⠀⠀⠀⡇⠀⢰⡿⠻⠶⠶⠶⠿⠤⢤⣏⣀⠀⠀⠸⡇⠀⡟⠉⠉⠉⠑⡶⢄⡀⠀⠀⠀
⠀⢀⣴⡯⣿⣯⢀⣁⢀⡼⠁⠀⢠⣠⣤⠤⠴⠇⠀⢸⠇⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠉⠓⠒⠢⠤⢄⣀⠀⠈⠡⢀⣵⣄⠀⠀
⠀⠈⣽⡿⠞⠋⠉⠉⠉⢀⣤⣔⡾⠿⢗⣿⣟⣤⢀⡼⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⠳⣤⡀⠀⡘⣧⠀
⠀⠀⠈⠀⠀⠀⠀⠀⠀⠀⠀⢀⡤⣶⠝⢋⣝⠗⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢳⡞⠛⢿⡆
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⠉⢀⣴⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡇⠐⢾⠇
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢤⣄⣀⠀⠀⠀⠀⢀⣀⠴⠁⢲⡾⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⠿⣭⣉⡉⠉⠉⣀⣠⠴⠟⠁⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠉⠉⠁⠀⠀⠀⠀⠀
Build by Joeri Abbo
"""


class BaseCommand:
    """Base class for extending CLI commands."""

    @staticmethod
    def register(command_group):
        raise NotImplementedError("Subclasses must implement the register method.")


@click.group()
@click.pass_context
def lizzy(ctx):
    """Lizzy CLI - A tool to manage Lizzy configurations and Datadog versions."""
    click.echo(ASCII_ART)
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


def auto_register_commands(group: click.Group):
    """Auto-register all command classes in the commands/ directory."""
    for _, module_name, is_pkg in pkgutil.iter_modules(commands.__path__):
        if is_pkg or module_name == "__init__" or module_name == "example_config":
            continue
        module = importlib.import_module(f"commands.{module_name}")
        for _, obj in inspect.getmembers(module):
            if (
                inspect.isclass(obj)
                and issubclass(obj, BaseCommand)
                and obj is not BaseCommand
            ):
                obj.register(group)


auto_register_commands(lizzy)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        click.echo(ASCII_ART)
        lizzy.main(args=["--help"], standalone_mode=False)
    else:
        lizzy()
