import click
import requests
import concurrent.futures
from lizzy.config import get_setting
import time

BASE_URL = "https://app.terraform.io"


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
    url = f"{BASE_URL}/api/v2/organizations/{organization}/workspaces"

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
    url = f"{BASE_URL}/api/v2/workspaces/{workspace_id}/notification-configurations"
    response = get_request(url)
    return response.json()["data"]


def create_slack_notification(workspace_id, webhook_url):
    """Create a Slack notification configuration for a workspace."""
    click.echo(f"Creating Slack notification for workspace {workspace_id}")
    url = f"{BASE_URL}/api/v2/workspaces/{workspace_id}/notification-configurations"
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


def cancel_run(run_id: str, status: str, workspace_name: str) -> None:
    """Cancel or discard a specific Terraform run based on its status."""
    run_link = f"{BASE_URL}/app/{get_organization()}/{workspace_name}/runs/{run_id}"
    
    # For planned status, try to discard first since that's the proper action
    if status == "planned":
        click.echo(f"Run {run_id} is in 'planned' status. Attempting to discard...")
        discard_url = f"{BASE_URL}/api/v2/runs/{run_id}/actions/discard"
        discard_response = requests.post(discard_url, headers=get_headers())
        
        if discard_response.status_code == 200:
            click.echo(f"✅ Successfully discarded run {run_id} (Status: {status})")
            return
        elif discard_response.status_code == 202:
            click.echo(f"✅ Discard initiated for run {run_id} (Status: {status})")
            return
        else:
            click.echo(f"⚠️  Failed to discard run {run_id}: {discard_response.status_code}. Attempting to cancel...")
    
    # Try to cancel the run (for non-planned runs or if discard failed)
    cancel_url = f"{BASE_URL}/api/v2/runs/{run_id}/actions/cancel"
    cancel_response = requests.post(cancel_url, headers=get_headers())

    if cancel_response.status_code == 200:
        click.echo(f"✅ Successfully cancelled run {run_id} (Status: {status})")
    elif cancel_response.status_code == 202:
        click.echo(f"✅ Cancellation initiated for run {run_id} (Status: {status})")
    elif cancel_response.status_code == 409:
        click.echo(f"⚠️  Run {run_id} is in a state that cannot be cancelled (Status: {status}). View it here: {run_link}")
    else:
        click.echo(f"❌ Failed to cancel run {run_id}: {cancel_response.status_code}. View it here: {run_link}")


def discard_plans() -> None:
    """Discard all non-terminal Terraform runs across all workspaces."""
    workspaces = get_workspaces()
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = []

        for workspace in workspaces:
            workspace_id = workspace["id"]
            workspace_name = workspace["attributes"]["name"]
            click.echo(
                f"Fetching non-terminal runs for workspace: {workspace_name} (ID: {workspace_id})"
            )

            runs = fetch_non_terminal_runs_for_workspace(workspace_id)

            for run in runs:
                run_id = run["id"]
                status = run["attributes"]["status"]

                click.echo(
                    f"Run {run_id} in workspace {workspace_name} is in status {status}. Attempting cancellation..."
                )
                futures.append(
                    executor.submit(cancel_run, run_id, status, workspace_name)
                )

        # Wait for all cancellation threads to complete
        for future in concurrent.futures.as_completed(futures):
            future.result()  # Raises any exceptions that occurred during execution


def fetch_non_terminal_runs_for_workspace(workspace_id: str) -> list:
    """Fetch non-terminal runs for a given workspace, skipping runs that are already in terminal states."""
    url = f"{BASE_URL}/api/v2/workspaces/{workspace_id}/runs"
    non_terminal_runs = []
    terminal_statuses = [
        "applied",
        "discarded",
        "errored",
        "canceled",
        "planned_and_finished",
    ]

    while url:
        response = requests.get(url, headers=get_headers())

        # Handle 429 Too Many Requests
        if response.status_code == 429:
            retry_after = int(
                response.headers.get("Retry-After", 10)
            )  # Default retry wait time of 10 seconds
            click.echo(f"Rate limit reached. Retrying after {retry_after} seconds...")
            time.sleep(retry_after)
            continue  # Retry the request after waiting

        # If successful, process the response
        if response.status_code == 200:
            runs = response.json()["data"]

            # Filter out terminal state runs and add only non-terminal runs
            non_terminal_on_page = [
                run
                for run in runs
                if run["attributes"]["status"] not in terminal_statuses
            ]

            if not non_terminal_on_page:
                # If all runs on this page are terminal, stop fetching more pages
                click.echo(
                    "All runs on this page are in terminal states. Stopping further fetches."
                )
                break

            non_terminal_runs.extend(non_terminal_on_page)
            url = response.json()["links"].get("next")
        else:
            click.echo(
                f"Error fetching runs for workspace {workspace_id}: {response.status_code}"
            )
            break

    return non_terminal_runs


def discard_run(run_id: str, status: str, workspace_name: str) -> None:
    """Discard a specific Terraform run."""
    discard_url = f"{BASE_URL}/api/v2/runs/{run_id}/actions/discard"
    discard_response = requests.post(discard_url, headers=get_headers())
    run_link = f"{BASE_URL}/app/{get_organization()}/{workspace_name}/runs/{run_id}"

    if discard_response.status_code == 200:
        click.echo(f"✅ Successfully discarded run {run_id} (Status: {status})")
    elif discard_response.status_code == 202:
        click.echo(f"✅ Discard initiated for run {run_id} (Status: {status})")
    else:
        click.echo(
            f"❌ Failed to discard run {run_id}: {discard_response.status_code}. View it here: {run_link}"
        )
