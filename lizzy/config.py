import click
import json
import subprocess
from pathlib import Path
import json
from pathlib import Path


def config_dir() -> str:   
    """Return the path to the config directory."""
    return Path.home() / ".lizzy"
def config_path() -> str:   
    """Return the path to the config file."""
    return config_dir() / "config.json"

def example_config_path() -> str:
    """Return the path to the example config file."""
    return Path(__file__).parent / "example_config.json"    

def get_config():
    """Load the config file, or the example config if it does not exist."""
    if config_path().exists():
        with open(config_path()) as f:
            config = json.load(f)
    else:
        with open(example_config_path()) as f:
            config = json.load(f)
    return config

def edit_config():
    """Create or open the config file in ~/.lizzy/config.json using vim."""
    if not config_path().exists():
        config_dir().mkdir(parents=True, exist_ok=True)
        with open(example_config_path()) as f:
            example_config = json.load(f)
        with open(config_path(), "w") as f:
            json.dump(example_config, f, indent=4)
        click.echo(f"Example config created at {config_path()}")
    try:
        subprocess.run(["vim", str(config_path())])
    except FileNotFoundError:
        click.echo(
            "vim is not installed or not found in PATH. Please install vim or open the config file manually."
        )

def get_setting(setting: str = None):
    """Get a specific setting from the config file."""
    split = setting.split(".") if setting else []
    
    if not split:
        return None
        
    config = get_config()
    for key in split:
        config = config.get(key)
        if config is None:
            return None
    return config