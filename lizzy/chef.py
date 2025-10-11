from lizzy.config import get_setting
from lizzy.github import get_tags_of_repo
# --- Compatibility Fixes (place before importing chef) ---
import collections
import collections.abc

if not hasattr(collections, "Mapping"):
    collections.Mapping = collections.abc.Mapping
if not hasattr(collections, "MutableMapping"):
    collections.MutableMapping = collections.abc.MutableMapping
if not hasattr(collections, "Sequence"):
    collections.Sequence = collections.abc.Sequence
# --- End Compatibility Fixes ---

from chef import ChefAPI, Environment
import chef


import click


def setup_chef_api() -> ChefAPI:
    """Set up and return a ChefAPI instance using configuration."""
    api = chef.autoconfigure()

    return api


def get_chef_environments() -> list:
    """Retrieve the list of Chef environments from configuration."""
    return get_setting("chef.environments")


def get_knife_config_path() -> str:
    """Retrieve the path to the knife configuration file from configuration."""
    return get_setting("chef.knife_config_path")

def get_chef_environment() -> str:
    """Get the Chef environment to modify."""
    environments = get_chef_environments()
    if not environments:
        raise ValueError("No Chef environments configured.")
    if len(environments) == 1:
        return environments[0]
    click.echo("Multiple Chef environments found:")
    for idx, env in enumerate(environments, start=1):
        click.echo(f"{idx}. {env}")
    choice = click.prompt("Select an environment by number", type=int)
    if 1 <= choice <= len(environments):
        return environments[choice - 1]
    else:
        raise ValueError("Invalid selection.")

def update_datadog_version() -> None:
    """Update the Datadog version in Chef configurations."""
    click.echo("Updating Datadog version in Chef configurations.")
    api = setup_chef_api()
    env = chef.Environment(get_chef_environment(), api=api)
    if click.confirm("Do you want to fetch the latest Datadog version from GitHub?"):
        new_version = get_latest_datadog_version().replace("v", "")
        if not new_version:
            click.echo("Could not fetch the latest Datadog version.")
            return
        click.echo(f"Latest Datadog version found: {new_version}")
    else:
        new_version = click.prompt("Enter the new Datadog version", type=str)
    click.echo(f"Updating Datadog version from {env.override_attributes.get('datadog', {}).get('agent_version', 'not set')} to {new_version}")
    click.confirm("Are you sure you want to proceed?", abort=True)
    env.override_attributes["datadog"]["agent_version"] = new_version
    env.save()

def update_chef_version() -> None:
    """Update the Chef version in Chef configurations."""
    click.echo("Updating Chef version in Chef configurations.")
    api = setup_chef_api()
    env = chef.Environment(get_chef_environment(), api=api)

    if "chef_client_updater" not in env.default_attributes:
        env.default_attributes["chef_client_updater"] = {}
    if click.confirm("Do you want to fetch the latest Chef version from GitHub?"):
        new_version = get_latest_chef_version().replace("v", "")
        if not new_version:
            click.echo("Could not fetch the latest Chef version.")
            return
        click.echo(f"Latest Chef version found: {new_version}")
    else:
        new_version = click.prompt("Enter the new Chef version", type=str)
        
    click.echo(f"Updating Chef version from {env.default_attributes.get('chef_client_updater', {}).get('version', 'not set')} to {new_version}")
    click.confirm("Are you sure you want to proceed?", abort=True)
    env.default_attributes["chef_client_updater"]["version"] = new_version
    env.save()


def get_latest_chef_version():
    """Fetch the latest Chef version from GitHub tags."""
    tags = get_tags_of_repo("chef/chef")
    if tags:
        return tags[0]
    return None

def get_latest_datadog_version():
    """Fetch the latest Datadog version from GitHub tags."""
    tags = get_tags_of_repo("DataDog/datadog-agent")
    if tags:
        return tags[0]
    return None
