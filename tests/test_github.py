"""Tests for lizzy.helpers.github module."""

from unittest.mock import MagicMock, patch

import pytest

from lizzy.helpers.github import get_tags_of_repo


class TestGetTagsOfRepo:
    """Test get_tags_of_repo function."""

    @patch("lizzy.helpers.github.requests.get")
    def test_get_tags_of_repo_returns_tag_names(self, mock_get):
        """Test that get_tags_of_repo returns list of tag names."""
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"name": "v1.2.3", "commit": {"sha": "abc123"}},
            {"name": "v1.2.2", "commit": {"sha": "def456"}},
            {"name": "v1.2.1", "commit": {"sha": "ghi789"}},
        ]
        mock_get.return_value = mock_response
        
        result = get_tags_of_repo("owner/repo")
        
        assert result == ["v1.2.3", "v1.2.2", "v1.2.1"]
        mock_get.assert_called_once_with("https://api.github.com/repos/owner/repo/tags")

    @patch("lizzy.helpers.github.requests.get")
    def test_get_tags_of_repo_all_tags_false_default(self, mock_get):
        """Test that get_tags_of_repo defaults to all_tags=False."""
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"name": "v2.0.0", "commit": {"sha": "xyz123"}},
        ]
        mock_get.return_value = mock_response
        
        result = get_tags_of_repo("owner/repo", all_tags=False)
        
        assert result == ["v2.0.0"]
        mock_get.assert_called_once_with("https://api.github.com/repos/owner/repo/tags")

    @patch("lizzy.helpers.github.requests.get")
    def test_get_tags_of_repo_all_tags_true_single_page(self, mock_get):
        """Test that get_tags_of_repo with all_tags=True handles single page."""
        # First call returns tags, second call returns empty list (end of pagination)
        mock_responses = [
            MagicMock(),  # First page
            MagicMock(),  # Second page (empty)
        ]
        mock_responses[0].json.return_value = [
            {"name": "v1.0.0", "commit": {"sha": "abc123"}},
            {"name": "v0.9.0", "commit": {"sha": "def456"}},
        ]
        mock_responses[1].json.return_value = []  # Empty response indicates end
        
        mock_get.side_effect = mock_responses
        
        result = get_tags_of_repo("owner/repo", all_tags=True)
        
        assert result == ["v1.0.0", "v0.9.0"]
        assert mock_get.call_count == 2
        mock_get.assert_any_call(
            "https://api.github.com/repos/owner/repo/tags",
            params={"page": 1, "per_page": 100}
        )
        mock_get.assert_any_call(
            "https://api.github.com/repos/owner/repo/tags",
            params={"page": 2, "per_page": 100}
        )

    @patch("lizzy.helpers.github.requests.get")
    def test_get_tags_of_repo_all_tags_true_multiple_pages(self, mock_get):
        """Test that get_tags_of_repo with all_tags=True handles multiple pages."""
        # Mock three pages: two with data, third empty
        mock_responses = [
            MagicMock(),  # Page 1
            MagicMock(),  # Page 2  
            MagicMock(),  # Page 3 (empty)
        ]
        
        mock_responses[0].json.return_value = [
            {"name": "v2.1.0", "commit": {"sha": "abc123"}},
            {"name": "v2.0.0", "commit": {"sha": "def456"}},
        ]
        mock_responses[1].json.return_value = [
            {"name": "v1.9.0", "commit": {"sha": "ghi789"}},
            {"name": "v1.8.0", "commit": {"sha": "jkl012"}},
        ]
        mock_responses[2].json.return_value = []  # End of pagination
        
        mock_get.side_effect = mock_responses
        
        result = get_tags_of_repo("owner/repo", all_tags=True)
        
        assert result == ["v2.1.0", "v2.0.0", "v1.9.0", "v1.8.0"]
        assert mock_get.call_count == 3
        
        # Verify all three API calls
        mock_get.assert_any_call(
            "https://api.github.com/repos/owner/repo/tags",
            params={"page": 1, "per_page": 100}
        )
        mock_get.assert_any_call(
            "https://api.github.com/repos/owner/repo/tags",
            params={"page": 2, "per_page": 100}
        )
        mock_get.assert_any_call(
            "https://api.github.com/repos/owner/repo/tags",
            params={"page": 3, "per_page": 100}
        )

    @patch("lizzy.helpers.github.requests.get")
    def test_get_tags_of_repo_empty_response(self, mock_get):
        """Test that get_tags_of_repo handles empty response."""
        mock_response = MagicMock()
        mock_response.json.return_value = []
        mock_get.return_value = mock_response
        
        result = get_tags_of_repo("owner/repo")
        
        assert result == []
        mock_get.assert_called_once()

    @patch("lizzy.helpers.github.requests.get")
    def test_get_tags_of_repo_all_tags_true_empty_first_page(self, mock_get):
        """Test that get_tags_of_repo with all_tags=True handles empty first page."""
        mock_response = MagicMock()
        mock_response.json.return_value = []
        mock_get.return_value = mock_response
        
        result = get_tags_of_repo("owner/repo", all_tags=True)
        
        assert result == []
        mock_get.assert_called_once_with(
            "https://api.github.com/repos/owner/repo/tags",
            params={"page": 1, "per_page": 100}
        )

    @patch("lizzy.helpers.github.requests.get")
    def test_get_tags_of_repo_handles_various_tag_formats(self, mock_get):
        """Test that get_tags_of_repo extracts names from various tag formats."""
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"name": "v1.0.0", "commit": {"sha": "abc123"}},
            {"name": "release-2.0", "commit": {"sha": "def456"}},
            {"name": "1.5.3", "commit": {"sha": "ghi789"}},
            {"name": "beta-3.0.0", "commit": {"sha": "jkl012"}},
        ]
        mock_get.return_value = mock_response
        
        result = get_tags_of_repo("owner/repo")
        
        assert result == ["v1.0.0", "release-2.0", "1.5.3", "beta-3.0.0"]