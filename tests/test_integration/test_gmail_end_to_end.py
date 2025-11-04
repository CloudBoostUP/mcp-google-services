"""End-to-end integration test for Gmail MCP server."""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from mcp_google_services.core.auth import AuthManager
from mcp_google_services.core.rate_limiter import RateLimiter
from mcp_google_services.services.gmail.api import GmailAPI
from mcp_google_services.services.gmail.backup import GmailBackup
from mcp_google_services.services.gmail.export import GmailExporter
from mcp_google_services.utils.config import Config


def test_complete_workflow():
    """Test complete Gmail backup workflow."""
    print("\n" + "="*80)
    print("Gmail MCP Server - End-to-End Integration Test")
    print("="*80 + "\n")
    
    # Step 1: Initialize configuration
    print("Step 1: Initializing configuration...")
    config = Config()
    print("✓ Configuration loaded")
    
    # Step 2: Authenticate
    print("\nStep 2: Authenticating with Gmail...")
    auth_manager = AuthManager(config=config)
    user_id = os.getenv("TEST_GMAIL_USER", "me")
    
    try:
        credentials = auth_manager.get_credentials(user_id)
        print(f"✓ Authentication successful for user: {user_id}")
    except FileNotFoundError as e:
        print(f"✗ Authentication failed: {e}")
        print("\nPlease ensure OAuth credentials are set up:")
        print("1. Download OAuth 2.0 credentials from Google Cloud Console")
        print("2. Place them in config/credentials.json")
        return False
    except Exception as e:
        print(f"✗ Authentication failed: {e}")
        return False
    
    # Step 3: Initialize Gmail API
    print("\nStep 3: Initializing Gmail API client...")
    gmail_api = GmailAPI(credentials=credentials)
    print("✓ Gmail API client initialized")
    
    # Step 4: Test API operations
    print("\nStep 4: Testing Gmail API operations...")
    try:
        # List messages
        print("  - Listing messages...")
        list_result = gmail_api.list_messages(user_id=user_id, max_results=5)
        message_count = len(list_result.get("messages", []))
        print(f"    ✓ Found {message_count} messages")
        
        # List labels
        print("  - Listing labels...")
        labels = gmail_api.list_labels(user_id=user_id)
        print(f"    ✓ Found {len(labels)} labels")
        
        # Get a message if available
        if message_count > 0:
            print("  - Getting message details...")
            message_id = list_result["messages"][0]["id"]
            message = gmail_api.get_message(user_id=user_id, message_id=message_id)
            print(f"    ✓ Retrieved message: {message_id}")
        
        print("✓ Gmail API operations successful")
    except Exception as e:
        print(f"✗ Gmail API operations failed: {e}")
        return False
    
    # Step 5: Test backup
    print("\nStep 5: Testing backup operations...")
    try:
        backup_service = GmailBackup(api=gmail_api, config=config)
        
        print("  - Running incremental backup (5 messages)...")
        backup_result = backup_service.incremental_backup(
            user_id=user_id,
            max_results=5
        )
        
        if backup_result.success:
            print(f"    ✓ Backup successful: {backup_result.message_count} messages")
            print(f"    ✓ Backup saved to: {backup_result.backup_path}")
        else:
            print(f"    ✗ Backup failed: {backup_result.error}")
            return False
        
        print("✓ Backup operations successful")
    except Exception as e:
        print(f"✗ Backup operations failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 6: Test export
    print("\nStep 6: Testing export operations...")
    try:
        exporter = GmailExporter(api=gmail_api)
        
        # Test MBOX export
        print("  - Testing MBOX export...")
        mbox_result = exporter.export_messages(
            user_id=user_id,
            output_path="test_output.mbox",
            format="mbox",
            max_results=3
        )
        print(f"    ✓ MBOX export: {mbox_result['message_count']} messages")
        
        # Test JSON export
        print("  - Testing JSON export...")
        json_result = exporter.export_messages(
            user_id=user_id,
            output_path="test_output.json",
            format="json",
            max_results=3
        )
        print(f"    ✓ JSON export: {json_result['message_count']} messages")
        
        # Test CSV export
        print("  - Testing CSV export...")
        csv_result = exporter.export_messages(
            user_id=user_id,
            output_path="test_output.csv",
            format="csv",
            max_results=3
        )
        print(f"    ✓ CSV export: {csv_result['message_count']} messages")
        
        print("✓ Export operations successful")
    except Exception as e:
        print(f"✗ Export operations failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 7: Cleanup test files
    print("\nStep 7: Cleaning up test files...")
    test_files = [
        "test_output.mbox",
        "test_output.json",
        "test_output.csv",
    ]
    
    for test_file in test_files:
        if Path(test_file).exists():
            Path(test_file).unlink()
            print(f"  ✓ Removed {test_file}")
    
    print("\n" + "="*80)
    print("✓ All tests passed! Gmail MCP server is working correctly.")
    print("="*80 + "\n")
    
    return True


if __name__ == "__main__":
    success = test_complete_workflow()
    sys.exit(0 if success else 1)

