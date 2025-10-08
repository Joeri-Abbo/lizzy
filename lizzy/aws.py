import gimme_aws_creds.main
import gimme_aws_creds.ui

from lizzy.config import get_setting


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
