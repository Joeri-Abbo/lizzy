"""Tests for lizzy.helpers.aws module."""

from unittest.mock import MagicMock, patch

import pytest

from lizzy.helpers.aws import get_account_by_name, get_aws_accounts, get_aws_credentials


class TestGetAwsAccounts:
    """Test get_aws_accounts function."""

    @patch("lizzy.helpers.aws.get_setting")
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

    @patch("lizzy.helpers.aws.get_setting")
    def test_get_aws_accounts_handles_empty_list(self, mock_get_setting):
        """Test that get_aws_accounts handles empty list."""
        mock_get_setting.return_value = []

        result = get_aws_accounts()

        assert result == []


class TestGetAccountByName:
    """Test get_account_by_name function."""

    @patch("lizzy.helpers.aws.get_aws_accounts")
    def test_get_account_by_name_returns_matching_account(self, mock_get_accounts):
        """Test that get_account_by_name returns the correct account."""
        accounts = [
            {"name": "dev", "id": "123456789"},
            {"name": "prod", "id": "987654321"},
        ]
        mock_get_accounts.return_value = accounts

        result = get_account_by_name("dev")

        assert result == {"name": "dev", "id": "123456789"}

    @patch("lizzy.helpers.aws.get_aws_accounts")
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

    @patch("lizzy.helpers.aws.get_aws_accounts")
    def test_get_account_by_name_handles_empty_list(self, mock_get_accounts):
        """Test that get_account_by_name handles empty account list."""
        mock_get_accounts.return_value = []

        with pytest.raises(ValueError):
            get_account_by_name("dev")


class TestGetAwsCredentials:
    """Test get_aws_credentials function."""

    @patch("lizzy.helpers.aws.get_account_by_name")
    @patch("lizzy.helpers.aws.gimme_aws_creds.ui.CLIUserInterface")
    @patch("lizzy.helpers.aws.gimme_aws_creds.main.GimmeAWSCreds")
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

    @patch("lizzy.helpers.aws.get_account_by_name")
    @patch("lizzy.helpers.aws.gimme_aws_creds.ui.CLIUserInterface")
    @patch("lizzy.helpers.aws.gimme_aws_creds.main.GimmeAWSCreds")
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

    @patch("lizzy.helpers.aws.get_account_by_name", side_effect=ValueError("Account not found"))
    def test_get_aws_credentials_propagates_account_error(self, mock_get_account):
        """Test that get_aws_credentials propagates account lookup errors."""
        with pytest.raises(ValueError) as exc_info:
            get_aws_credentials("nonexistent")

        assert "Account not found" in str(exc_info.value)


class TestGetClusters:
    """Test get_clusters function."""

    @patch("lizzy.helpers.aws.boto3.client")
    def test_get_clusters_returns_cluster_list(self, mock_boto_client):
        """Test that get_clusters returns list of ECS clusters."""
        mock_ecs = MagicMock()
        mock_boto_client.return_value = mock_ecs
        
        mock_paginator = MagicMock()
        mock_ecs.get_paginator.return_value = mock_paginator
        mock_paginator.paginate.return_value = [
            {"clusterArns": ["cluster-1", "cluster-2"]},
            {"clusterArns": ["cluster-3"]},
        ]
        
        from lizzy.helpers.aws import get_clusters
        result = get_clusters("key", "secret", "token")
        
        assert result == ["cluster-1", "cluster-2", "cluster-3"]
        mock_boto_client.assert_called_once_with(
            "ecs",
            aws_access_key_id="key",
            aws_secret_access_key="secret",
            aws_session_token="token"
        )

    @patch("lizzy.helpers.aws.boto3.client")
    @patch("lizzy.helpers.aws.click.echo")
    def test_get_clusters_handles_boto_error(self, mock_echo, mock_boto_client):
        """Test that get_clusters handles boto3 errors gracefully."""
        from botocore.exceptions import ClientError
        
        mock_ecs = MagicMock()
        mock_boto_client.return_value = mock_ecs
        mock_ecs.get_paginator.side_effect = ClientError(
            {"Error": {"Code": "AccessDenied", "Message": "Access denied"}},
            "ListClusters"
        )
        
        from lizzy.helpers.aws import get_clusters
        result = get_clusters("key", "secret", "token")
        
        assert result == []
        mock_echo.assert_called_once()
        assert "Error fetching clusters:" in mock_echo.call_args[0][0]


class TestChooseCluster:
    """Test choose_cluster function."""

    @patch("lizzy.helpers.aws.click.prompt")
    @patch("lizzy.helpers.aws.click.echo")
    def test_choose_cluster_returns_selected_cluster(self, mock_echo, mock_prompt):
        """Test that choose_cluster returns the selected cluster."""
        clusters = ["cluster-1", "cluster-2", "cluster-3"]
        mock_prompt.return_value = "2"
        
        from lizzy.helpers.aws import choose_cluster
        result = choose_cluster(clusters)
        
        assert result == "cluster-2"
        mock_echo.assert_called()
        mock_prompt.assert_called_once_with("Select a cluster [1-3]: ")

    @patch("lizzy.helpers.aws.click.prompt")
    @patch("lizzy.helpers.aws.click.echo")
    def test_choose_cluster_handles_invalid_then_valid_input(self, mock_echo, mock_prompt):
        """Test that choose_cluster handles invalid input then valid input."""
        clusters = ["cluster-1", "cluster-2"]
        mock_prompt.side_effect = ["invalid", "0", "3", "1"]
        
        from lizzy.helpers.aws import choose_cluster
        result = choose_cluster(clusters)
        
        assert result == "cluster-1"
        assert mock_prompt.call_count == 4


class TestGetFargateServices:
    """Test get_fargate_services function."""

    @patch("lizzy.helpers.aws.boto3.client")
    def test_get_fargate_services_returns_service_list(self, mock_boto_client):
        """Test that get_fargate_services returns list of services."""
        mock_ecs = MagicMock()
        mock_boto_client.return_value = mock_ecs
        
        mock_paginator = MagicMock()
        mock_ecs.get_paginator.return_value = mock_paginator
        mock_paginator.paginate.return_value = [
            {"serviceArns": ["service-1", "service-2"]},
            {"serviceArns": ["service-3"]},
        ]
        
        from lizzy.helpers.aws import get_fargate_services
        result = get_fargate_services("cluster-1", "key", "secret", "token")
        
        assert result == ["service-1", "service-2", "service-3"]
        mock_paginator.paginate.assert_called_once_with(cluster="cluster-1")

    @patch("lizzy.helpers.aws.boto3.client")
    @patch("lizzy.helpers.aws.click.echo")
    def test_get_fargate_services_handles_error(self, mock_echo, mock_boto_client):
        """Test that get_fargate_services handles errors gracefully."""
        from botocore.exceptions import BotoCoreError
        
        mock_ecs = MagicMock()
        mock_boto_client.return_value = mock_ecs
        mock_ecs.get_paginator.side_effect = BotoCoreError()
        
        from lizzy.helpers.aws import get_fargate_services
        result = get_fargate_services("cluster-1", "key", "secret", "token")
        
        assert result == []
        mock_echo.assert_called_once()
        assert "Error fetching services:" in mock_echo.call_args[0][0]


class TestChooseService:
    """Test choose_service function."""

    @patch("lizzy.helpers.aws.click.prompt")
    @patch("lizzy.helpers.aws.click.echo")
    def test_choose_service_returns_selected_service(self, mock_echo, mock_prompt):
        """Test that choose_service returns the selected service."""
        services = ["service-1", "service-2", "service-3"]
        mock_prompt.return_value = "3"
        
        from lizzy.helpers.aws import choose_service
        result = choose_service(services)
        
        assert result == "service-3"
        mock_echo.assert_called()
        mock_prompt.assert_called_once_with("Select a service [1-3]: ")


class TestEcsForceRedeploy:
    """Test ecs_force_redeploy function."""

    @patch("lizzy.helpers.aws.boto3.client")
    @patch("lizzy.helpers.aws.click.echo")
    def test_ecs_force_redeploy_triggers_deployment(self, mock_echo, mock_boto_client):
        """Test that ecs_force_redeploy triggers force deployment."""
        mock_ecs = MagicMock()
        mock_boto_client.return_value = mock_ecs
        
        mock_ecs.describe_services.return_value = {
            "services": [{"taskDefinition": "task-def-1"}]
        }
        
        from lizzy.helpers.aws import ecs_force_redeploy
        ecs_force_redeploy("cluster-1", "service-1", "key", "secret", "token")
        
        mock_ecs.describe_services.assert_called_once_with(
            cluster="cluster-1", 
            services=["service-1"]
        )
        mock_ecs.update_service.assert_called_once_with(
            cluster="cluster-1",
            service="service-1",
            taskDefinition="task-def-1",
            forceNewDeployment=True,
        )
        assert mock_echo.call_count >= 2

    @patch("lizzy.helpers.aws.boto3.client")
    @patch("builtins.print")
    def test_ecs_force_redeploy_handles_service_not_found(self, mock_print, mock_boto_client):
        """Test that ecs_force_redeploy handles service not found."""
        mock_ecs = MagicMock()
        mock_boto_client.return_value = mock_ecs
        
        mock_ecs.describe_services.return_value = {"services": []}
        
        from lizzy.helpers.aws import ecs_force_redeploy
        ecs_force_redeploy("cluster-1", "service-1", "key", "secret", "token")
        
        mock_print.assert_called_once_with("Service not found.")
        mock_ecs.update_service.assert_not_called()

    @patch("lizzy.helpers.aws.boto3.client")
    @patch("lizzy.helpers.aws.click.echo")
    def test_ecs_force_redeploy_handles_error(self, mock_echo, mock_boto_client):
        """Test that ecs_force_redeploy handles boto3 errors."""
        from botocore.exceptions import ClientError
        
        mock_ecs = MagicMock()
        mock_boto_client.return_value = mock_ecs
        mock_ecs.describe_services.side_effect = ClientError(
            {"Error": {"Code": "ServiceNotFound", "Message": "Service not found"}},
            "DescribeServices"
        )
        
        from lizzy.helpers.aws import ecs_force_redeploy
        ecs_force_redeploy("cluster-1", "service-1", "key", "secret", "token")
        
        mock_echo.assert_called()
        assert "Error forcing redeploy:" in mock_echo.call_args[0][0]


class TestRunAwsFargateRestart:
    """Test run_aws_fargate_restart function."""

    @patch("lizzy.helpers.aws.get_aws_credentials")
    @patch("lizzy.helpers.aws.get_config_accounts")
    @patch("lizzy.helpers.aws.get_clusters")
    @patch("lizzy.helpers.aws.choose_cluster")
    @patch("lizzy.helpers.aws.get_fargate_services")
    @patch("lizzy.helpers.aws.ecs_force_redeploy")
    @patch("lizzy.helpers.aws.click.echo")
    def test_run_aws_fargate_restart_all_services(
        self, mock_echo, mock_redeploy, mock_get_services, mock_choose_cluster,
        mock_get_clusters, mock_get_accounts, mock_get_creds
    ):
        """Test that run_aws_fargate_restart restarts all services when all_services=True."""
        mock_get_accounts.return_value = "dev"
        mock_get_creds.return_value = ("key", "secret", "token", "arn")
        mock_get_clusters.return_value = ["cluster-1"]
        mock_choose_cluster.return_value = "cluster-1"
        mock_get_services.return_value = ["service-1", "service-2"]
        
        from lizzy.helpers.aws import run_aws_fargate_restart
        run_aws_fargate_restart(all_services=True)
        
        assert mock_redeploy.call_count == 2
        mock_redeploy.assert_any_call("cluster-1", "service-1", "key", "secret", "token")
        mock_redeploy.assert_any_call("cluster-1", "service-2", "key", "secret", "token")

    @patch("lizzy.helpers.aws.get_aws_credentials")
    @patch("lizzy.helpers.aws.get_config_accounts")
    @patch("lizzy.helpers.aws.get_clusters")
    @patch("lizzy.helpers.aws.click.echo")
    def test_run_aws_fargate_restart_no_clusters(
        self, mock_echo, mock_get_clusters, mock_get_accounts, mock_get_creds
    ):
        """Test that run_aws_fargate_restart handles no clusters found."""
        mock_get_accounts.return_value = "dev"
        mock_get_creds.return_value = ("key", "secret", "token", "arn")
        mock_get_clusters.return_value = []
        
        from lizzy.helpers.aws import run_aws_fargate_restart
        run_aws_fargate_restart()
        
        mock_echo.assert_any_call("No ECS clusters found.")

    @patch("lizzy.helpers.aws.get_aws_credentials")
    @patch("lizzy.helpers.aws.get_config_accounts")
    @patch("lizzy.helpers.aws.get_clusters")
    @patch("lizzy.helpers.aws.choose_cluster")
    @patch("lizzy.helpers.aws.get_fargate_services")
    @patch("lizzy.helpers.aws.choose_service")
    @patch("lizzy.helpers.aws.ecs_force_redeploy")
    @patch("lizzy.helpers.aws.click.echo")
    def test_run_aws_fargate_restart_single_service(
        self, mock_echo, mock_redeploy, mock_choose_service, mock_get_services,
        mock_choose_cluster, mock_get_clusters, mock_get_accounts, mock_get_creds
    ):
        """Test that run_aws_fargate_restart restarts single service when all_services=False."""
        mock_get_accounts.return_value = "dev"
        mock_get_creds.return_value = ("key", "secret", "token", "arn")
        mock_get_clusters.return_value = ["cluster-1"]
        mock_choose_cluster.return_value = "cluster-1"
        mock_get_services.return_value = ["service-1", "service-2"]
        mock_choose_service.return_value = "service-1"
        
        from lizzy.helpers.aws import run_aws_fargate_restart
        run_aws_fargate_restart(all_services=False)
        
        mock_redeploy.assert_called_once_with("cluster-1", "service-1", "key", "secret", "token")
        mock_choose_service.assert_called_once_with(["service-1", "service-2"])

    @patch("lizzy.helpers.aws.get_aws_credentials")
    @patch("lizzy.helpers.aws.get_config_accounts")
    @patch("lizzy.helpers.aws.get_clusters")
    @patch("lizzy.helpers.aws.choose_cluster")
    @patch("lizzy.helpers.aws.get_fargate_services")
    @patch("lizzy.helpers.aws.click.echo")
    def test_run_aws_fargate_restart_no_services(
        self, mock_echo, mock_get_services, mock_choose_cluster,
        mock_get_clusters, mock_get_accounts, mock_get_creds
    ):
        """Test that run_aws_fargate_restart handles no services found."""
        mock_get_accounts.return_value = "dev"
        mock_get_creds.return_value = ("key", "secret", "token", "arn")
        mock_get_clusters.return_value = ["cluster-1"]
        mock_choose_cluster.return_value = "cluster-1"
        mock_get_services.return_value = []
        
        from lizzy.helpers.aws import run_aws_fargate_restart
        run_aws_fargate_restart()
        
        mock_echo.assert_any_call("No services found in the selected cluster.")
