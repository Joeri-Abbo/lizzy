import json
import re

import click
import requests

from lizzy.config import get_setting
from lizzy.gitlab import setup_gitlab


def get_auth_token(registry: str, repository: str) -> str:
    """Get an authentication token for the ECR registry."""
    auth_url = f"https://public.ecr.aws/token/?service=public.ecr.aws&scope=repository:{registry}/{repository}:pull"
    response = requests.get(auth_url)
    response.raise_for_status()
    token = response.json()["token"]
    return token


def get_ecr_tags(registry: str, repository: str) -> list[str]:
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


def get_fetch_versions() -> dict:
    """Fetch the versions of the Datadog agent."""
    registry = "datadog"
    repository = "agent"
    tags = get_ecr_tags(registry, repository)
    pattern = re.compile(r"^\d+\.\d+\.\d+$")

    return [tag for tag in tags if pattern.match(tag)]


def print_fetch_versions() -> None:
    """Fetch the versions of the Datadog agent."""
    for tag in sorted(get_fetch_versions()):
        click.echo(f"Datadog Agent: {tag}")


def get_highest_version() -> str:
    """Get the highest version of the Datadog agent."""
    versions = get_fetch_versions()
    return max(versions, key=lambda v: list(map(int, v.split("."))))


def bump_datadog_components(version: str) -> None:
    """Bump the Datadog components to a specific version."""
    components = get_setting("gitlab.components")
    username = get_setting("gitlab.username")
    email = get_setting("gitlab.email")
    components = components if components else []
    gl = setup_gitlab()
    for component in components:
        try:
            click.echo(f"Bumping Datadog in component: {component['name']}")

            project = gl.projects.get(component["project_name_with_namespace"])
            click.echo(f"Project: {project.name} - {component['branch']}")
            path = "modules/fargate/templates/container_definition.tpl"

            file = project.files.get(file_path=path, ref=component["branch"])
            template = file.decode().decode("utf-8")

            image = get_datadog_image(json.loads(filter_content(template)))

            if not image:
                return False, "No datadog tag found"
            message = f"Update datadog to {version} from {image.split(':')[-1]}"
            click.echo(f"Message: {message}")
            feature_branch = f"feature/update-datadog-{version}"

            # Create feature branch from the develop branch
            project.branches.create(
                {"branch": feature_branch, "ref": component["branch"]}
            )

            commit_data = {
                "branch": feature_branch,
                "commit_message": message,
                "actions": [],
                "author_name": username,
                "author_email": email,
            }

            commit_data["actions"].append(
                {
                    "action": "update",
                    "file_path": path,
                    "content": template.replace(
                        image,
                        f"580117755768.dkr.ecr.eu-central-1.amazonaws.com/public.ecr.aws/datadog/agent:{version}",
                    ),
                }
            )
            project.commits.create(commit_data)

            merge_request = project.mergerequests.create(
                {
                    "source_branch": feature_branch,
                    "target_branch": component["branch"],
                    "title": message,
                }
            )

            click.echo(f"Merge request created: {merge_request.web_url}")
        except Exception as e:
            click.echo(f"Failed to bump Datadog in {component['name']}: {e}")


def filter_content(content: str) -> str:
    """Filter content based on regex"""
    content = content.strip()
    if content.startswith("${jsonencode("):
        content = content[len("${jsonencode(") :]
    if content.endswith(")}"):
        content = content[:-2]
    return re.sub(r"#.*", "", content)


def get_datadog_image(items: list) -> str:
    """Get datadog tag from content"""
    for item in items:
        if item["name"] == "datadog-agent":
            return filter_content(item["image"])

    return ""
