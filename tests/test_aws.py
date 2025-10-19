"""Tests for lizzy.aws module."""

from unittest.mock import MagicMock, patch

import pytest

from lizzy.helpers.aws import get_account_by_name, get_aws_accounts, get_aws_credentials


class TestGetAwsAccounts:
    """Test get_aws_accounts function."""

    @patch("lizzy.aws.get_setting")
    def test_get_aws_accounts_returns_list(self, mock_get_setting):
        """Test that get_aws_accounts returns the accounts list from settings."""
        expected_accounts = [
            {"name": "dev", "id": "123456789"},
            {"name": "prod", "id": "987654321"},
        ]
        mock_get_setting.return_value = expected_accounts

        result = get_aws_accounts()

        assert result == expected_accounts
        mock_get_setting.assert_called_once_with("aws.accounts")

    @patch("lizzy.aws.get_setting")
    def test_get_aws_accounts_handles_empty_list(self, mock_get_setting):
        """Test that get_aws_accounts handles empty list."""
        mock_get_setting.return_value = []

        result = get_aws_accounts()

        assert result == []


class TestGetAccountByName:
    """Test get_account_by_name function."""

    @patch("lizzy.aws.get_aws_accounts")
    def test_get_account_by_name_returns_matching_account(self, mock_get_accounts):
        """Test that get_account_by_name returns the correct account."""
        accounts = [
            {"name": "dev", "id": "123456789"},
            {"name": "prod", "id": "987654321"},
        ]
        mock_get_accounts.return_value = accounts

        result = get_account_by_name("dev")

        assert result == {"name": "dev", "id": "123456789"}

    @patch("lizzy.aws.get_aws_accounts")
    def test_get_account_by_name_raises_error_for_missing_account(
        self, mock_get_accounts
    ):
        """Test that get_account_by_name raises ValueError for non-existent account."""
        accounts = [
            {"name": "dev", "id": "123456789"},
            {"name": "prod", "id": "987654321"},
        ]
        mock_get_accounts.return_value = accounts

        with pytest.raises(ValueError) as exc_info:
            get_account_by_name("staging")

        assert "Account with name staging not found" in str(exc_info.value)

    @patch("lizzy.aws.get_aws_accounts")
    def test_get_account_by_name_handles_empty_list(self, mock_get_accounts):
        """Test that get_account_by_name handles empty account list."""
        mock_get_accounts.return_value = []

        with pytest.raises(ValueError):
            get_account_by_name("dev")


class TestGetAwsCredentials:
    """Test get_aws_credentials function."""

    @patch("lizzy.aws.get_account_by_name")
    @patch("lizzy.aws.gimme_aws_creds.ui.CLIUserInterface")
    @patch("lizzy.aws.gimme_aws_creds.main.GimmeAWSCreds")
    def test_get_aws_credentials_returns_credentials_tuple(
        self, mock_gimme_creds, mock_ui, mock_get_account
    ):
        """Test that get_aws_credentials returns a tuple of credentials."""
        mock_get_account.return_value = {"name": "dev", "id": "123456789"}

        mock_creds_instance = MagicMock()
        mock_gimme_creds.return_value = mock_creds_instance

        mock_creds_data = {
            "credentials": {
                "aws_access_key_id": "AKIAIOSFODNN7EXAMPLE",
                "aws_secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
                "aws_session_token": "FwoGZXIvYXdzEBQaDExample==",
            },
            "role": {"arn": "arn:aws:iam::123456789:role/test-role"},
        }

        mock_creds_instance.iter_selected_aws_credentials.return_value = iter(
            [mock_creds_data]
        )

        result = get_aws_credentials("dev")

        assert isinstance(result, tuple)
        assert len(result) == 4
        assert result[0] == "AKIAIOSFODNN7EXAMPLE"
        assert result[1] == "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
        assert result[2] == "FwoGZXIvYXdzEBQaDExample=="
        assert result[3] == "arn:aws:iam::123456789:role/test-role"

    @patch("lizzy.aws.get_account_by_name")
    @patch("lizzy.aws.gimme_aws_creds.ui.CLIUserInterface")
    @patch("lizzy.aws.gimme_aws_creds.main.GimmeAWSCreds")
    def test_get_aws_credentials_formats_pattern_correctly(
        self, mock_gimme_creds, mock_ui, mock_get_account
    ):
        """Test that get_aws_credentials formats the role pattern correctly."""
        mock_get_account.return_value = {"name": "dev", "id": "123456789"}

        mock_creds_instance = MagicMock()
        mock_gimme_creds.return_value = mock_creds_instance

        mock_creds_data = {
            "credentials": {
                "aws_access_key_id": "AKIAIOSFODNN7EXAMPLE",
                "aws_secret_access_key": "secret",
                "aws_session_token": "token",
            },
            "role": {"arn": "arn"},
        }

        mock_creds_instance.iter_selected_aws_credentials.return_value = iter(
            [mock_creds_data]
        )

        get_aws_credentials("dev")

        # Verify UI was called with correct pattern
        mock_ui.assert_called_once()
        call_args = mock_ui.call_args[1]["argv"]
        assert "--roles" in call_args
        assert "/:(123456789):/" in call_args

    @patch("lizzy.aws.get_account_by_name", side_effect=ValueError("Account not found"))
    def test_get_aws_credentials_propagates_account_error(self, mock_get_account):
        """Test that get_aws_credentials propagates account lookup errors."""
        with pytest.raises(ValueError) as exc_info:
            get_aws_credentials("nonexistent")

        assert "Account not found" in str(exc_info.value)
