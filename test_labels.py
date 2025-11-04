#!/usr/bin/env python3
"""Quick test script to list Gmail labels."""

import sys
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mcp_google_services.utils.config import Config
from mcp_google_services.core.auth import AuthManager
from mcp_google_services.services.gmail.api import GmailAPI


async def test_list_labels():
    """Test listing Gmail labels."""
    print("🔐 Authenticating...")
    
    # Try direct ADC first
    from google.auth import default as google_auth_default
    from google.auth.exceptions import DefaultCredentialsError
    
    try:
        print("  Trying Application Default Credentials...")
        credentials, project = google_auth_default(scopes=[
            "https://www.googleapis.com/auth/gmail.readonly",
            "https://www.googleapis.com/auth/gmail.readonly"
        ])
        print(f"  ✅ Direct ADC successful! Credentials valid: {credentials.valid}")
        if not credentials.valid:
            print("  ⚠️  Credentials not valid, attempting refresh...")
            from google.auth.transport.requests import Request
            credentials.refresh(Request())
            print("  ✅ Refresh successful!")
    except DefaultCredentialsError as e:
        print(f"  ❌ ADC not available: {e}")
        print("\n  Trying AuthManager...")
        config = Config()
        auth_manager = AuthManager(config=config)
        try:
            credentials = auth_manager.get_credentials("me")
            print("✅ Authentication via AuthManager successful!")
        except Exception as e2:
            print(f"❌ AuthManager failed: {e2}")
            return
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n📋 Fetching Gmail labels...")
    gmail_api = GmailAPI(credentials=credentials)
    
    try:
        labels = gmail_api.list_labels(user_id="me")
        print(f"\n✅ Found {len(labels)} labels:\n")
        for label in labels:
            name = label.get("name", "Unknown")
            label_id = label.get("id", "N/A")
            label_type = label.get("type", "user")
            print(f"  • {name} (ID: {label_id}, Type: {label_type})")
    except Exception as e:
        print(f"❌ Error listing labels: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_list_labels())

