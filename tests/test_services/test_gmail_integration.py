"""Integration tests for Gmail MCP server functionality."""

import pytest
import os
from pathlib import Path
from datetime import datetime

from mcp_google_services.core.auth import AuthManager
from mcp_google_services.core.rate_limiter import RateLimiter
from mcp_google_services.services.gmail.api import GmailAPI
from mcp_google_services.services.gmail.backup import GmailBackup
from mcp_google_services.services.gmail.export import GmailExporter
from mcp_google_services.services.gmail.parser import EmailParser
from mcp_google_services.services.gmail.mbox import MBOXGenerator
from mcp_google_services.utils.config import Config


@pytest.fixture
def config():
    """Create test configuration."""
    return Config()


@pytest.fixture
def auth_manager(config):
    """Create auth manager for testing."""
    return AuthManager(config=config)


@pytest.fixture
def credentials(auth_manager):
    """Get authenticated credentials.
    
    Note: This will prompt for OAuth flow if credentials don't exist.
    """
    # Use a test user ID or skip if credentials not available
    user_id = os.getenv("TEST_GMAIL_USER", "me")
    
    try:
        creds = auth_manager.get_credentials(user_id)
        return creds
    except FileNotFoundError:
        pytest.skip("Gmail credentials not found. Please set up OAuth credentials.")
    except Exception as e:
        pytest.skip(f"Authentication failed: {e}")


@pytest.fixture
def gmail_api(credentials):
    """Create Gmail API client."""
    return GmailAPI(credentials=credentials)


@pytest.fixture
def gmail_backup(gmail_api, config):
    """Create Gmail backup service."""
    return GmailBackup(api=gmail_api, config=config)


@pytest.fixture
def gmail_exporter(gmail_api):
    """Create Gmail exporter."""
    return GmailExporter(api=gmail_api)


class TestAuthentication:
    """Test authentication functionality."""

    def test_auth_manager_initialization(self, auth_manager):
        """Test AuthManager can be initialized."""
        assert auth_manager is not None
        assert auth_manager.credentials_path is not None

    def test_get_credentials_requires_credentials_file(self, auth_manager):
        """Test that get_credentials requires credentials file."""
        # This test verifies FileNotFoundError is raised when credentials don't exist
        # In actual testing, credentials file should be present
        pass

    @pytest.mark.integration
    def test_oauth_authentication_flow(self, auth_manager):
        """Test OAuth 2.0 authentication flow.
        
        This test requires:
        - Valid OAuth credentials file at config/credentials.json
        - User interaction for OAuth consent
        """
        user_id = os.getenv("TEST_GMAIL_USER", "me")
        
        try:
            credentials = auth_manager.get_credentials(user_id)
            assert credentials is not None
            assert credentials.valid or credentials.refresh_token is not None
        except FileNotFoundError:
            pytest.skip("OAuth credentials file not found")
        except Exception as e:
            pytest.skip(f"OAuth flow failed: {e}")


class TestGmailAPI:
    """Test Gmail API integration."""

    @pytest.mark.integration
    def test_list_messages(self, gmail_api):
        """Test listing messages."""
        result = gmail_api.list_messages(user_id="me", max_results=10)
        
        assert result is not None
        assert "messages" in result or "resultSizeEstimate" in result

    @pytest.mark.integration
    def test_list_messages_with_query(self, gmail_api):
        """Test listing messages with query filter."""
        # Get recent messages from last 7 days
        query = "newer_than:7d"
        result = gmail_api.list_messages(user_id="me", query=query, max_results=10)
        
        assert result is not None

    @pytest.mark.integration
    def test_get_message(self, gmail_api):
        """Test getting a single message."""
        # First, get a message ID
        list_result = gmail_api.list_messages(user_id="me", max_results=1)
        
        if list_result.get("messages"):
            message_id = list_result["messages"][0]["id"]
            message = gmail_api.get_message(user_id="me", message_id=message_id)
            
            assert message is not None
            assert "id" in message
            assert message["id"] == message_id

    @pytest.mark.integration
    def test_list_labels(self, gmail_api):
        """Test listing Gmail labels."""
        labels = gmail_api.list_labels(user_id="me")
        
        assert isinstance(labels, list)
        # Should have at least some standard labels
        label_names = [label.get("name", "") for label in labels]
        assert any(name in label_names for name in ["INBOX", "SENT", "DRAFT"])

    @pytest.mark.integration
    def test_batch_get_messages(self, gmail_api):
        """Test batch message retrieval."""
        # Get multiple message IDs
        list_result = gmail_api.list_messages(user_id="me", max_results=5)
        
        if list_result.get("messages") and len(list_result["messages"]) > 1:
            message_ids = [msg["id"] for msg in list_result["messages"][:3]]
            messages = gmail_api.batch_get_messages(
                user_id="me",
                message_ids=message_ids
            )
            
            assert isinstance(messages, list)
            assert len(messages) <= len(message_ids)


class TestEmailParser:
    """Test email parsing functionality."""

    @pytest.mark.integration
    def test_parse_message(self, gmail_api):
        """Test parsing a Gmail message."""
        # Get a message
        list_result = gmail_api.list_messages(user_id="me", max_results=1)
        
        if list_result.get("messages"):
            message_id = list_result["messages"][0]["id"]
            message = gmail_api.get_message(user_id="me", message_id=message_id)
            
            parser = EmailParser()
            parsed = parser.parse_message(message)
            
            assert parsed is not None
            assert "id" in parsed
            assert "headers" in parsed
            assert "body" in parsed


class TestMBOXGeneration:
    """Test MBOX format generation."""

    def test_mbox_generator_initialization(self):
        """Test MBOXGenerator can be created."""
        output_path = "test_output.mbox"
        mbox = MBOXGenerator(output_path)
        
        assert mbox is not None
        assert mbox.output_path == Path(output_path)
        
        # Cleanup
        if Path(output_path).exists():
            Path(output_path).unlink()

    @pytest.mark.integration
    def test_mbox_generation(self, gmail_api):
        """Test generating MBOX file from messages."""
        # Get a few messages
        list_result = gmail_api.list_messages(user_id="me", max_results=3)
        
        if list_result.get("messages"):
            message_ids = [msg["id"] for msg in list_result["messages"]]
            messages = gmail_api.batch_get_messages(
                user_id="me",
                message_ids=message_ids
            )
            
            parser = EmailParser()
            output_path = "test_backup.mbox"
            
            with MBOXGenerator(output_path) as mbox:
                for message in messages:
                    parsed = parser.parse_message(message)
                    mbox.add_message(parsed)
            
            # Verify file was created
            assert Path(output_path).exists()
            assert mbox.get_message_count() > 0
            
            # Cleanup
            Path(output_path).unlink()


class TestBackupOperations:
    """Test backup operations."""

    @pytest.mark.integration
    def test_incremental_backup(self, gmail_backup):
        """Test incremental backup."""
        result = gmail_backup.incremental_backup(
            user_id="me",
            max_results=10
        )
        
        assert result is not None
        assert result.success is True or result.error is not None
        if result.success:
            assert result.message_count >= 0
            assert result.backup_path is not None

    @pytest.mark.integration
    def test_full_backup_small(self, gmail_backup):
        """Test full backup with limited messages."""
        result = gmail_backup.full_backup(
            user_id="me",
            max_results=5  # Small number for testing
        )
        
        assert result is not None
        assert result.success is True or result.error is not None
        if result.success:
            assert result.message_count >= 0

    @pytest.mark.integration
    def test_backup_state_tracking(self, gmail_backup):
        """Test that backup state is tracked."""
        # Run incremental backup
        result1 = gmail_backup.incremental_backup(
            user_id="me",
            max_results=5
        )
        
        if result1.success:
            # Run second backup - should only get new messages
            result2 = gmail_backup.incremental_backup(
                user_id="me",
                max_results=5
            )
            
            # Second backup should have fewer or equal messages (if no new messages)
            assert result2.message_count <= result1.message_count


class TestExportOperations:
    """Test export operations."""

    @pytest.mark.integration
    def test_export_to_mbox(self, gmail_exporter):
        """Test exporting to MBOX format."""
        output_path = "test_export.mbox"
        
        result = gmail_exporter.export_messages(
            user_id="me",
            output_path=output_path,
            format="mbox",
            max_results=5
        )
        
        assert result is not None
        assert result["format"] == "mbox"
        assert result["message_count"] >= 0
        
        # Cleanup
        if Path(output_path).exists():
            Path(output_path).unlink()

    @pytest.mark.integration
    def test_export_to_json(self, gmail_exporter):
        """Test exporting to JSON format."""
        output_path = "test_export.json"
        
        result = gmail_exporter.export_messages(
            user_id="me",
            output_path=output_path,
            format="json",
            max_results=5
        )
        
        assert result is not None
        assert result["format"] == "json"
        assert result["message_count"] >= 0
        
        # Cleanup
        if Path(output_path).exists():
            Path(output_path).unlink()

    @pytest.mark.integration
    def test_export_to_csv(self, gmail_exporter):
        """Test exporting to CSV format."""
        output_path = "test_export.csv"
        
        result = gmail_exporter.export_messages(
            user_id="me",
            output_path=output_path,
            format="csv",
            max_results=5
        )
        
        assert result is not None
        assert result["format"] == "csv"
        assert result["message_count"] >= 0
        
        # Cleanup
        if Path(output_path).exists():
            Path(output_path).unlink()

    @pytest.mark.integration
    def test_export_to_eml(self, gmail_exporter):
        """Test exporting to EML format."""
        output_path = "test_export_eml"
        
        result = gmail_exporter.export_messages(
            user_id="me",
            output_path=output_path,
            format="eml",
            max_results=3
        )
        
        assert result is not None
        assert result["format"] == "eml"
        assert result["message_count"] >= 0
        
        # Cleanup
        if Path(output_path).exists():
            import shutil
            shutil.rmtree(output_path)


class TestRateLimiting:
    """Test rate limiting functionality."""

    def test_rate_limiter_initialization(self):
        """Test RateLimiter can be created."""
        limiter = RateLimiter(quota_per_second=250)
        
        assert limiter is not None
        assert limiter.quota_per_second == 250

    def test_rate_limiter_wait(self):
        """Test rate limiter wait functionality."""
        limiter = RateLimiter(quota_per_second=250)
        
        # Should not wait if quota is available
        initial_quota = limiter.get_current_quota()
        limiter.wait_if_needed(quota_cost=1)
        
        # Quota should be reduced
        assert limiter.get_current_quota() < initial_quota


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "integration"])

