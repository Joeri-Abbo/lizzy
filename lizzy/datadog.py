import click
import re

import requests


def get_auth_token(registry:str, repository:str) -> str:
    """Get an authentication token for the ECR registry."""
    auth_url = f"https://public.ecr.aws/token/?service=public.ecr.aws&scope=repository:{registry}/{repository}:pull"
    response = requests.get(auth_url)
    response.raise_for_status()
    token = response.json()["token"]
    return token


def get_ecr_tags(registry:str, repository:str) -> list[str]:
    """Get the list of tags for a given ECR repository."""
    token = get_auth_token(registry, repository)
    url = f"https://public.ecr.aws/v2/{registry}/{repository}/tags/list"
    headers = {"Authorization": f"Bearer {token}"}

    tags = []
    next_token = None

    while True:
        params = {}
        if next_token:
            params["next"] = next_token

        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        tags.extend(data.get("tags", []))

        next_token = data.get("next")
        if not next_token:
            break

    return tags

def get_fetch_versions()-> dict:
    """Fetch the versions of the Datadog agent."""
    registry = "datadog"
    repository = "agent"
    tags = get_ecr_tags(registry, repository)
    pattern = re.compile(r"^\d+\.\d+\.\d+$")

    return  [tag for tag in tags if pattern.match(tag)]

def print_fetch_versions() -> None:
    """Fetch the versions of the Datadog agent."""
    for tag in sorted(get_fetch_versions()):
        click.echo(f"Datadog Agent: {tag}")

