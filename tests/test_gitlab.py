"""Tests for lizzy.gitlab module."""

from unittest.mock import MagicMock, patch

import pytest

from lizzy.gitlab import (
    develop_to_main,
    fetch_approved_merge_requests,
    main_to_develop,
    remove_merged_branches,
    setup_gitlab,
)


class TestSetupGitlab:
    """Test setup_gitlab function."""

    @patch("lizzy.gitlab.get_setting")
    @patch("lizzy.gitlab.gitlab.Gitlab")
    def test_setup_gitlab_returns_gitlab_instance(self, mock_gitlab, mock_get_setting):
        """Test that setup_gitlab returns a configured GitLab instance."""
        mock_get_setting.return_value = "test_token_123"
        mock_gl_instance = MagicMock()
        mock_gitlab.return_value = mock_gl_instance

        result = setup_gitlab()

        assert result == mock_gl_instance
        mock_get_setting.assert_called_once_with("gitlab.api_token")
        mock_gitlab.assert_called_once_with(
            "https://gitlab.com", private_token="test_token_123"
        )

    @patch("lizzy.gitlab.get_setting")
    def test_setup_gitlab_raises_error_when_token_missing(self, mock_get_setting):
        """Test that setup_gitlab raises ValueError when API token is missing."""
        mock_get_setting.return_value = None

        with pytest.raises(ValueError) as exc_info:
            setup_gitlab()

        assert "GitLab API token is not set" in str(exc_info.value)


class TestDevelopToMain:
    """Test develop_to_main function."""

    @patch("lizzy.gitlab.get_setting")
    @patch("lizzy.gitlab.setup_gitlab")
    @patch("builtins.print")
    def test_develop_to_main_creates_merge_requests(
        self, mock_print, mock_setup_gitlab, mock_get_setting
    ):
        """Test that develop_to_main creates merge requests for all components."""
        components = [
            {
                "name": "component1",
                "project_name_with_namespace": "group/project1",
            },
            {
                "name": "component2",
                "project_name_with_namespace": "group/project2",
            },
        ]
        mock_get_setting.return_value = components

        mock_gl = MagicMock()
        mock_setup_gitlab.return_value = mock_gl

        mock_project1 = MagicMock()
        mock_project2 = MagicMock()
        mock_gl.projects.get.side_effect = [mock_project1, mock_project2]

        mock_mr1 = MagicMock(web_url="https://gitlab.com/mr/1")
        mock_mr2 = MagicMock(web_url="https://gitlab.com/mr/2")
        mock_project1.mergerequests.create.return_value = mock_mr1
        mock_project2.mergerequests.create.return_value = mock_mr2

        develop_to_main()

        assert mock_project1.mergerequests.create.call_count == 1
        assert mock_project2.mergerequests.create.call_count == 1

        # Verify merge request parameters
        call_args = mock_project1.mergerequests.create.call_args[0][0]
        assert call_args["source_branch"] == "develop"
        assert call_args["target_branch"] == "main"
        assert call_args["title"] == "Develop to main"

    @patch("lizzy.gitlab.get_setting")
    @patch("lizzy.gitlab.setup_gitlab")
    @patch("builtins.print")
    def test_develop_to_main_handles_errors(
        self, mock_print, mock_setup_gitlab, mock_get_setting
    ):
        """Test that develop_to_main handles errors gracefully."""
        components = [
            {
                "name": "component1",
                "project_name_with_namespace": "group/project1",
            }
        ]
        mock_get_setting.return_value = components

        mock_gl = MagicMock()
        mock_setup_gitlab.return_value = mock_gl

        mock_gl.projects.get.side_effect = Exception("Project not found")

        develop_to_main()

        # Verify error was printed
        error_calls = [c for c in mock_print.call_args_list if "Failed" in str(c)]
        assert len(error_calls) > 0

    @patch("lizzy.gitlab.get_setting")
    @patch("lizzy.gitlab.setup_gitlab")
    def test_develop_to_main_handles_empty_components(
        self, mock_setup_gitlab, mock_get_setting
    ):
        """Test that develop_to_main handles empty components list."""
        mock_get_setting.return_value = None

        mock_gl = MagicMock()
        mock_setup_gitlab.return_value = mock_gl

        develop_to_main()

        mock_gl.projects.get.assert_not_called()


class TestMainToDevelop:
    """Test main_to_develop function."""

    @patch("lizzy.gitlab.get_setting")
    @patch("lizzy.gitlab.setup_gitlab")
    @patch("builtins.print")
    def test_main_to_develop_creates_merge_requests(
        self, mock_print, mock_setup_gitlab, mock_get_setting
    ):
        """Test that main_to_develop creates merge requests for all components."""
        components = [
            {
                "name": "component1",
                "project_name_with_namespace": "group/project1",
            }
        ]
        mock_get_setting.return_value = components

        mock_gl = MagicMock()
        mock_setup_gitlab.return_value = mock_gl

        mock_project = MagicMock()
        mock_gl.projects.get.return_value = mock_project

        mock_mr = MagicMock(web_url="https://gitlab.com/mr/1")
        mock_project.mergerequests.create.return_value = mock_mr

        main_to_develop()

        # Verify merge request parameters
        call_args = mock_project.mergerequests.create.call_args[0][0]
        assert call_args["source_branch"] == "main"
        assert call_args["target_branch"] == "develop"
        assert call_args["title"] == "Main to Develop"


class TestRemoveMergedBranches:
    """Test remove_merged_branches function."""

    @patch("lizzy.gitlab.get_setting")
    @patch("lizzy.gitlab.setup_gitlab")
    @patch("click.echo")
    def test_remove_merged_branches_deletes_merged_branches(
        self, mock_echo, mock_setup_gitlab, mock_get_setting
    ):
        """Test that remove_merged_branches deletes merged branches."""
        mock_get_setting.return_value = "group_id_123"

        mock_gl = MagicMock()
        mock_setup_gitlab.return_value = mock_gl

        mock_group = MagicMock()
        mock_gl.groups.get.return_value = mock_group

        mock_project = MagicMock(id="project_1", name="Test Project")
        mock_group.projects.list.return_value = [mock_project]

        mock_proj = MagicMock()
        mock_gl.projects.get.return_value = mock_proj

        # Create mock branches with spec to avoid name attribute issues
        branch1 = MagicMock()
        branch1.name = "feature/test"
        branch1.merged = True

        branch2 = MagicMock()
        branch2.name = "main"
        branch2.merged = False

        branch3 = MagicMock()
        branch3.name = "develop"
        branch3.merged = False

        branch4 = MagicMock()
        branch4.name = "feature/old"
        branch4.merged = True

        mock_proj.branches.list.return_value = [branch1, branch2, branch3, branch4]

        remove_merged_branches()

        # Should only delete merged non-protected branches
        assert mock_proj.branches.delete.call_count == 2
        mock_proj.branches.delete.assert_any_call("feature/test")
        mock_proj.branches.delete.assert_any_call("feature/old")

    @patch("lizzy.gitlab.get_setting")
    @patch("lizzy.gitlab.setup_gitlab")
    @patch("click.echo")
    def test_remove_merged_branches_handles_errors(
        self, mock_echo, mock_setup_gitlab, mock_get_setting
    ):
        """Test that remove_merged_branches handles deletion errors gracefully."""
        mock_get_setting.return_value = "group_id_123"

        mock_gl = MagicMock()
        mock_setup_gitlab.return_value = mock_gl

        mock_group = MagicMock()
        mock_gl.groups.get.return_value = mock_group

        mock_project = MagicMock(id="project_1", name="Test Project")
        mock_group.projects.list.return_value = [mock_project]

        mock_proj = MagicMock()
        mock_gl.projects.get.return_value = mock_proj

        branch1 = MagicMock()
        branch1.name = "feature/test"
        branch1.merged = True
        mock_proj.branches.list.return_value = [branch1]
        mock_proj.branches.delete.side_effect = Exception("Protected branch")

        remove_merged_branches()

        # Verify error was echoed
        error_calls = [c for c in mock_echo.call_args_list if "Failed" in str(c)]
        assert len(error_calls) > 0


class TestFetchApprovedMergeRequests:
    """Test fetch_approved_merge_requests function."""

    @patch("lizzy.gitlab.get_setting")
    @patch("lizzy.gitlab.setup_gitlab")
    @patch("click.echo")
    @patch("builtins.input")
    def test_fetch_approved_merge_requests_merges_on_confirmation(
        self, mock_input, mock_echo, mock_setup_gitlab, mock_get_setting
    ):
        """Test that fetch_approved_merge_requests merges on user confirmation."""
        mock_get_setting.side_effect = lambda key: {
            "gitlab.approval_group_id": "group_123",
            "gitlab.username": "testuser",
        }.get(key)

        mock_gl = MagicMock()
        mock_setup_gitlab.return_value = mock_gl

        mock_group = MagicMock()
        mock_gl.groups.get.return_value = mock_group

        mock_project = MagicMock(id="project_1", name="Test Project")
        mock_group.projects.list.return_value = [mock_project]

        mock_proj = MagicMock()
        mock_gl.projects.get.return_value = mock_proj

        # Create mock merge request
        mock_mr = MagicMock(
            iid=1,
            title="Test MR",
            web_url="https://gitlab.com/mr/1",
            author={"username": "testuser"},
        )
        mock_proj.mergerequests.list.return_value = [mock_mr]

        mock_mr_detail = MagicMock()
        mock_proj.mergerequests.get.return_value = mock_mr_detail

        # Mock pipeline
        mock_pipeline = MagicMock(status="success")
        mock_mr_detail.pipelines.list.return_value = [mock_pipeline]

        # Mock approvals
        mock_approvals = MagicMock()
        mock_approvals.approved_by = [{"user": {"username": "approver"}}]
        mock_mr_detail.approvals.get.return_value = mock_approvals

        mock_input.return_value = "y"

        fetch_approved_merge_requests(yolo=False)

        mock_mr_detail.merge.assert_called_once()

    @patch("lizzy.gitlab.get_setting")
    @patch("lizzy.gitlab.setup_gitlab")
    @patch("click.echo")
    def test_fetch_approved_merge_requests_auto_merges_with_yolo(
        self, mock_echo, mock_setup_gitlab, mock_get_setting
    ):
        """Test that fetch_approved_merge_requests auto-merges with yolo flag."""
        mock_get_setting.side_effect = lambda key: {
            "gitlab.approval_group_id": "group_123",
            "gitlab.username": "testuser",
        }.get(key)

        mock_gl = MagicMock()
        mock_setup_gitlab.return_value = mock_gl

        mock_group = MagicMock()
        mock_gl.groups.get.return_value = mock_group

        mock_project = MagicMock(id="project_1", name="Test Project")
        mock_group.projects.list.return_value = [mock_project]

        mock_proj = MagicMock()
        mock_gl.projects.get.return_value = mock_proj

        mock_mr = MagicMock(
            iid=1,
            title="Test MR",
            web_url="https://gitlab.com/mr/1",
            author={"username": "testuser"},
        )
        mock_proj.mergerequests.list.return_value = [mock_mr]

        mock_mr_detail = MagicMock()
        mock_proj.mergerequests.get.return_value = mock_mr_detail

        mock_pipeline = MagicMock(status="success")
        mock_mr_detail.pipelines.list.return_value = [mock_pipeline]

        mock_approvals = MagicMock()
        mock_approvals.approved_by = [{"user": {"username": "approver"}}]
        mock_mr_detail.approvals.get.return_value = mock_approvals

        fetch_approved_merge_requests(yolo=True)

        mock_mr_detail.merge.assert_called_once()

    @patch("lizzy.gitlab.get_setting")
    @patch("lizzy.gitlab.setup_gitlab")
    @patch("click.echo")
    def test_fetch_approved_merge_requests_skips_failed_pipelines(
        self, mock_echo, mock_setup_gitlab, mock_get_setting
    ):
        """Test that fetch_approved_merge_requests skips MRs with failed pipelines."""
        mock_get_setting.side_effect = lambda key: {
            "gitlab.approval_group_id": "group_123",
            "gitlab.username": "testuser",
        }.get(key)

        mock_gl = MagicMock()
        mock_setup_gitlab.return_value = mock_gl

        mock_group = MagicMock()
        mock_gl.groups.get.return_value = mock_group

        mock_project = MagicMock(id="project_1", name="Test Project")
        mock_group.projects.list.return_value = [mock_project]

        mock_proj = MagicMock()
        mock_gl.projects.get.return_value = mock_proj

        mock_mr = MagicMock(
            iid=1,
            title="Test MR",
            web_url="https://gitlab.com/mr/1",
            author={"username": "testuser"},
        )
        mock_proj.mergerequests.list.return_value = [mock_mr]

        mock_mr_detail = MagicMock()
        mock_proj.mergerequests.get.return_value = mock_mr_detail

        mock_pipeline = MagicMock(status="failed")
        mock_mr_detail.pipelines.list.return_value = [mock_pipeline]

        fetch_approved_merge_requests(yolo=True)

        mock_mr_detail.merge.assert_not_called()
