#!/usr/bin/env python3
"""Manual test script for Gmail MCP server.

This script provides an interactive way to test the Gmail MCP server functionality
without requiring pytest setup. Run this script to test authentication, API calls,
backup, and export operations.

Usage:
    python test_gmail_server.py

Environment Variables:
    TEST_GMAIL_USER: Gmail user email (default: "me")
    GOOGLE_APPLICATION_CREDENTIALS: Path to OAuth credentials JSON file
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mcp_google_services.core.auth import AuthManager
from mcp_google_services.core.rate_limiter import RateLimiter
from mcp_google_services.services.gmail.api import GmailAPI
from mcp_google_services.services.gmail.backup import GmailBackup
from mcp_google_services.services.gmail.export import GmailExporter
from mcp_google_services.utils.config import Config


def print_header(text: str):
    """Print a formatted header."""
    print("\n" + "="*80)
    print(f"  {text}")
    print("="*80)


def print_success(message: str):
    """Print success message."""
    print(f"✓ {message}")


def print_error(message: str):
    """Print error message."""
    print(f"✗ {message}")


def print_info(message: str):
    """Print info message."""
    print(f"  {message}")


def test_authentication():
    """Test authentication."""
    print_header("Testing Authentication")
    
    config = Config()
    auth_manager = AuthManager(config=config)
    user_id = os.getenv("TEST_GMAIL_USER", "me")
    
    print_info(f"Attempting to authenticate user: {user_id}")
    print_info(f"Credentials path: {auth_manager.credentials_path}")
    
    try:
        if not auth_manager.credentials_path.exists():
            print_error(f"Credentials file not found: {auth_manager.credentials_path}")
            print_info("Please download OAuth 2.0 credentials from Google Cloud Console")
            print_info("and place them in config/credentials.json")
            return None, None
        
        credentials = auth_manager.get_credentials(user_id)
        
        if credentials and (credentials.valid or credentials.refresh_token):
            print_success("Authentication successful!")
            print_info(f"Token valid: {credentials.valid}")
            print_info(f"Has refresh token: {credentials.refresh_token is not None}")
            return credentials, user_id
        else:
            print_error("Authentication failed - invalid credentials")
            return None, None
            
    except Exception as e:
        print_error(f"Authentication failed: {e}")
        import traceback
        traceback.print_exc()
        return None, None


def test_gmail_api(credentials, user_id: str):
    """Test Gmail API operations."""
    print_header("Testing Gmail API Operations")
    
    try:
        gmail_api = GmailAPI(credentials=credentials)
        print_success("Gmail API client initialized")
        
        # Test 1: List messages
        print_info("Test 1: Listing messages (max 5)...")
        list_result = gmail_api.list_messages(user_id=user_id, max_results=5)
        message_count = len(list_result.get("messages", []))
        print_success(f"Found {message_count} messages")
        
        if message_count > 0:
            print_info(f"  First message ID: {list_result['messages'][0]['id']}")
        
        # Test 2: List labels
        print_info("Test 2: Listing labels...")
        labels = gmail_api.list_labels(user_id=user_id)
        print_success(f"Found {len(labels)} labels")
        
        # Show some label names
        if labels:
            label_names = [label.get("name", "") for label in labels[:5]]
            print_info(f"  Sample labels: {', '.join(label_names)}")
        
        # Test 3: Get a message
        if message_count > 0:
            print_info("Test 3: Getting message details...")
            message_id = list_result["messages"][0]["id"]
            message = gmail_api.get_message(user_id=user_id, message_id=message_id)
            print_success(f"Retrieved message: {message_id}")
            print_info(f"  Snippet: {message.get('snippet', '')[:50]}...")
        
        # Test 4: Batch get messages
        if message_count > 1:
            print_info("Test 4: Batch getting messages...")
            message_ids = [msg["id"] for msg in list_result["messages"][:3]]
            messages = gmail_api.batch_get_messages(
                user_id=user_id,
                message_ids=message_ids
            )
            print_success(f"Retrieved {len(messages)} messages in batch")
        
        print_success("All Gmail API tests passed!")
        return gmail_api
        
    except Exception as e:
        print_error(f"Gmail API test failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_backup(gmail_api, user_id: str):
    """Test backup operations."""
    print_header("Testing Backup Operations")
    
    try:
        config = Config()
        backup_service = GmailBackup(api=gmail_api, config=config)
        print_success("Backup service initialized")
        
        # Test incremental backup
        print_info("Test 1: Running incremental backup (max 5 messages)...")
        result = backup_service.incremental_backup(
            user_id=user_id,
            max_results=5
        )
        
        if result.success:
            print_success(f"Backup completed: {result.message_count} messages")
            print_info(f"  Backup path: {result.backup_path}")
            print_info(f"  Messages processed: {result.messages_processed}")
            print_info(f"  Messages failed: {result.messages_failed}")
            
            # Check file exists
            if Path(result.backup_path).exists():
                file_size = Path(result.backup_path).stat().st_size
                print_info(f"  File size: {file_size:,} bytes")
                print_success("Backup file created successfully!")
            else:
                print_error("Backup file not found!")
        else:
            print_error(f"Backup failed: {result.error}")
            return False
        
        print_success("Backup operations test passed!")
        return True
        
    except Exception as e:
        print_error(f"Backup test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_export(gmail_api, user_id: str):
    """Test export operations."""
    print_header("Testing Export Operations")
    
    try:
        exporter = GmailExporter(api=gmail_api)
        print_success("Export service initialized")
        
        # Test MBOX export
        print_info("Test 1: Exporting to MBOX format (3 messages)...")
        mbox_result = exporter.export_messages(
            user_id=user_id,
            output_path="test_export.mbox",
            format="mbox",
            max_results=3
        )
        print_success(f"MBOX export: {mbox_result['message_count']} messages")
        print_info(f"  Output: {mbox_result['output_path']}")
        
        # Test JSON export
        print_info("Test 2: Exporting to JSON format (3 messages)...")
        json_result = exporter.export_messages(
            user_id=user_id,
            output_path="test_export.json",
            format="json",
            max_results=3
        )
        print_success(f"JSON export: {json_result['message_count']} messages")
        print_info(f"  Output: {json_result['output_path']}")
        
        # Test CSV export
        print_info("Test 3: Exporting to CSV format (3 messages)...")
        csv_result = exporter.export_messages(
            user_id=user_id,
            output_path="test_export.csv",
            format="csv",
            max_results=3
        )
        print_success(f"CSV export: {csv_result['message_count']} messages")
        print_info(f"  Output: {csv_result['output_path']}")
        
        print_success("Export operations test passed!")
        return True
        
    except Exception as e:
        print_error(f"Export test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def cleanup_test_files():
    """Clean up test files."""
    print_header("Cleaning Up Test Files")
    
    test_files = [
        "test_export.mbox",
        "test_export.json",
        "test_export.csv",
    ]
    
    cleaned = 0
    for test_file in test_files:
        path = Path(test_file)
        if path.exists():
            path.unlink()
            print_success(f"Removed {test_file}")
            cleaned += 1
    
    if cleaned == 0:
        print_info("No test files to clean up")
    else:
        print_success(f"Cleaned up {cleaned} test file(s)")


def main():
    """Run all tests."""
    print_header("Gmail MCP Server - Manual Test Suite")
    
    print_info("This script will test:")
    print_info("  1. Authentication")
    print_info("  2. Gmail API integration")
    print_info("  3. Backup operations")
    print_info("  4. Export operations")
    print_info("")
    print_info("Prerequisites:")
    print_info("  - OAuth 2.0 credentials file at: config/credentials.json")
    print_info("  - Gmail API enabled in Google Cloud Project")
    print_info("  - Gmail account with test emails")
    print_info("")
    
    input("Press Enter to continue or Ctrl+C to cancel...")
    
    # Test authentication
    credentials, user_id = test_authentication()
    if not credentials:
        print("\n" + "="*80)
        print("✗ Tests failed at authentication step")
        print("="*80)
        return False
    
    # Test Gmail API
    gmail_api = test_gmail_api(credentials, user_id)
    if not gmail_api:
        print("\n" + "="*80)
        print("✗ Tests failed at Gmail API step")
        print("="*80)
        return False
    
    # Test backup
    backup_ok = test_backup(gmail_api, user_id)
    if not backup_ok:
        print("\n" + "="*80)
        print("✗ Tests failed at backup step")
        print("="*80)
        return False
    
    # Test export
    export_ok = test_export(gmail_api, user_id)
    if not export_ok:
        print("\n" + "="*80)
        print("✗ Tests failed at export step")
        print("="*80)
        return False
    
    # Cleanup
    cleanup_test_files()
    
    # Final summary
    print_header("Test Summary")
    print_success("All tests passed!")
    print_info("✓ Authentication: Working")
    print_info("✓ Gmail API: Working")
    print_info("✓ Backup Operations: Working")
    print_info("✓ Export Operations: Working")
    print("")
    print("Gmail MCP server is ready for use!")
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

