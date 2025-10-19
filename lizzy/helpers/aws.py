import gimme_aws_creds.main
import gimme_aws_creds.ui
import click
from lizzy.helpers.config import get_setting
import boto3
from botocore.exceptions import BotoCoreError, ClientError


def get_aws_credentials(account_name: str) -> tuple:
    """Authenticate AWS CLI using the account name."""

    account = get_account_by_name(account_name)

    pattern = "|".join(sorted({account["id"]}))
    pattern = f"/:({pattern}):/"
    ui = gimme_aws_creds.ui.CLIUserInterface(argv=["", "--roles", pattern])
    creds = gimme_aws_creds.main.GimmeAWSCreds(ui=ui)
    creds = creds.iter_selected_aws_credentials().__next__()
    return (
        creds["credentials"]["aws_access_key_id"],
        creds["credentials"]["aws_secret_access_key"],
        creds["credentials"]["aws_session_token"],
        creds["role"]["arn"],
    )


def get_account_by_name(account_name: str) -> dict:
    """Retrieve AWS account details by name."""
    accounts = get_aws_accounts()
    for account in accounts:
        if account["name"] == account_name:
            return account
    raise ValueError(f"Account with name {account_name} not found.")


def get_aws_accounts() -> list:
    """Retrieve a list of AWS accounts."""
    return get_setting("aws.accounts")


def get_config_accounts() -> list:
    """Retrieve a list of AWS accounts from the config file."""
    accounts = get_aws_accounts()
    labels = ""
    for account in accounts:
        labels += f"{account['id']} | {account['name']}\n"
    account_name = click.prompt(
        f"Select an AWS account to authenticate \n\n{labels}\n",
        type=click.Choice([str(f"{account['name']}") for account in accounts]),
        show_choices=True,
    )
    return account_name


def get_clusters(
        aws_access_key_id: str,
        aws_secret_access_key: str,
        aws_session_token: str):
    """Retrieve a list of ECS clusters."""
    ecs = boto3.client("ecs",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        aws_session_token=aws_session_token,)
    try:
        clusters = []
        paginator = ecs.get_paginator("list_clusters")
        for page in paginator.paginate():
            clusters.extend(page.get("clusterArns", []))
        return clusters
    except (BotoCoreError, ClientError) as e:
        click.echo(f"Error fetching clusters: {e}")
        return []


def choose_cluster(clusters: list) -> str:
    """Prompt user to choose a cluster from the list."""
    click.echo("Available ECS Clusters:")
    for idx, cluster in enumerate(clusters):
        click.echo(f"{idx + 1}: {cluster}")
    while True:
        choice = click.prompt(f"Select a cluster [1-{len(clusters)}]: ")
        if choice.isdigit() and 1 <= int(choice) <= len(clusters):
            return clusters[int(choice) - 1]
        click.echo("Invalid selection. Try again.")


def get_fargate_services(cluster: str, aws_access_key_id: str, aws_secret_access_key: str, aws_session_token: str) -> list:
    """Retrieve a list of Fargate services in a cluster."""
    ecs = boto3.client("ecs",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        aws_session_token=aws_session_token,)
    try:
        services = []
        paginator = ecs.get_paginator("list_services")
        for page in paginator.paginate(cluster=cluster):
            services.extend(page.get("serviceArns", []))
        return services
    except (BotoCoreError, ClientError) as e:
        click.echo(f"Error fetching services: {e}")
        return []


def choose_service(services: list) -> str:
    """Prompt user to choose a service from the list."""
    click.echo("Available ECS Services:")
    for idx, service in enumerate(services):
        click.echo(f"{idx + 1}: {service}")
    while True:
        choice = click.prompt(f"Select a service [1-{len(services)}]: ")
        if choice.isdigit() and 1 <= int(choice) <= len(services):
            return services[int(choice) - 1]
        click.echo("Invalid selection. Try again.")


def ecs_force_redeploy(
    cluster,
    service,
    aws_access_key_id,
    aws_secret_access_key,
    aws_session_token,
):
    """Force redeploy an ECS service."""
    ecs = boto3.client(
        "ecs",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        aws_session_token=aws_session_token,
    )
    try:
        response = ecs.describe_services(cluster=cluster, services=[service])
        if not response["services"]:
            print("Service not found.")
            return
        task_def = response["services"][0]["taskDefinition"]
        click.echo(f"Forcing new deployment for service: {service}")
        ecs.update_service(
            cluster=cluster,
            service=service,
            taskDefinition=task_def,
            forceNewDeployment=True,
        )
        click.echo("Force redeploy triggered.")
    except (BotoCoreError, ClientError) as e:
        click.echo(f"Error forcing redeploy: {e}")



def run_aws_fargate_restart(all_services: bool=True)-> None:
    """Restart AWS Fargate tasks."""
    (
                aws_access_key_id,
                aws_secret_access_key,
                aws_session_token,
                role_arn,
    ) = get_aws_credentials(get_config_accounts())

    clusters = get_clusters(
        aws_access_key_id,
        aws_secret_access_key,
        aws_session_token,
    )
    if not clusters:
        click.echo("No ECS clusters found.")
        return
    cluster = choose_cluster(clusters)
    services = get_fargate_services(
        cluster,
        aws_access_key_id,
        aws_secret_access_key,
        aws_session_token,
    )
    if not services:
        click.echo("No services found in the selected cluster.")
        return
    click.echo(
        f"Force redeploying all {len(services)} services in cluster {cluster}..."
    )
    if all_services:
        for service in services:
            ecs_force_redeploy(
                cluster,
                service,
                aws_access_key_id,
                aws_secret_access_key,
                aws_session_token,
            )
            click.echo("Force redeploy triggered for all services.")
    else:
        service = choose_service(services)
        ecs_force_redeploy(
            cluster,
            service,
            aws_access_key_id,
            aws_secret_access_key,
            aws_session_token,
        )
        click.echo("Force redeploy triggered for the selected service.")
