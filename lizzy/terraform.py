import click
import requests

from lizzy.config import get_setting


def get_organization() -> str:
    """Retrieve the Terraform organization from settings."""
    return get_setting("terraform.organization")


def get_headers() -> dict:
    """Generate headers for Terraform API requests."""
    api_token = get_setting("terraform.api_token")
    return {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/vnd.api+json",
    }


def get_request(url: str):
    """Make a GET request to the specified URL with appropriate headers."""
    headers = get_headers()
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response


def post_request(url: str, payload: dict):
    """Make a POST request to the specified URL with appropriate headers and payload."""
    headers = get_headers()
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response


def get_workspaces():
    """Retrieve all workspaces from a given organization, handling pagination."""
    all_workspaces = []
    organization = get_organization()
    url = f"https://app.terraform.io/api/v2/organizations/{organization}/workspaces"

    # Initial call to start the loop
    print(f"Retrieving workspaces from {organization}")
    print(f"GET {url}")
    response = get_request(url)
    page = response.json()

    while True:
        all_workspaces.extend(page["data"])

        # Follow pagination link if 'next' exists, else break
        if "next" in page["links"] and page["links"]["next"]:
            click.echo(f"GET {page['links']['next']}")
            response = get_request(page["links"]["next"])
            page = response.json()
        else:
            break

    return all_workspaces


def get_notifications(workspace_id):
    """Retrieve all notification configurations for a workspace."""
    url = f"https://app.terraform.io/api/v2/workspaces/{workspace_id}/notification-configurations"
    response = get_request(url)
    return response.json()["data"]


def create_slack_notification(workspace_id, webhook_url):
    """Create a Slack notification configuration for a workspace."""
    click.echo(f"Creating Slack notification for workspace {workspace_id}")
    url = f"https://app.terraform.io/api/v2/workspaces/{workspace_id}/notification-configurations"
    payload = {
        "data": {
            "type": "notification-configurations",
            "attributes": {
                "enabled": True,
                "name": "Slack Notification",
                "destination-type": "slack",
                "triggers": [
                    "run:created",
                    "run:planning",
                    "run:needs_attention",
                    "run:applying",
                    "run:completed",
                    "run:errored",
                ],
                "url": webhook_url,
            },
        }
    }
    response = post_request(url, json=payload)
    return response.status_code == 201


def set_slack_webhook() -> None:
    """Set the Slack webhook URL for Terraform."""
    slack_webhook_url = get_setting("terraform.slack_webhook_url")
    if not slack_webhook_url:
        raise ValueError("Slack webhook URL is not set in the configuration.")

    for workspace in get_workspaces():
        click.echo(f"Checking workspace {workspace['attributes']['name']}")
        workspace_id = workspace["id"]
        notifications = get_notifications(workspace_id)
        slack_configured = any(
            n["attributes"]["destination-type"] == "slack" for n in notifications
        )

        if not slack_configured:
            result = create_slack_notification(workspace_id, slack_webhook_url)
            if result:
                click.echo(
                    f"Slack webhook added to workspace {workspace['attributes']['name']}"
                )
            else:
                click.echo(
                    f"Failed to add Slack webhook to workspace {workspace['attributes']['name']}"
                )
        else:
            click.echo(
                f"Slack webhook already configured for workspace {workspace['attributes']['name']}"
            )
