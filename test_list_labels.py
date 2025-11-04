#!/usr/bin/env python3
"""Test script to list Gmail labels."""

import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from mcp_google_services.utils.config import Config
from mcp_google_services.core.auth import AuthManager
from mcp_google_services.services.gmail.api import GmailAPI


def main():
    print("🔐 Authenticating...")
    config = Config()
    auth_manager = AuthManager(config=config)
    
    try:
        credentials = auth_manager.get_credentials("me")
        print("✅ Authentication successful!")
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return
    
    print("\n📋 Fetching Gmail labels...")
    gmail_api = GmailAPI(credentials=credentials)
    
    try:
        labels = gmail_api.list_labels(user_id="me")
        print(f"\n✅ Found {len(labels)} labels:\n")
        
        # Sort labels: system labels first, then user labels
        system_labels = [l for l in labels if l.get("type") == "system"]
        user_labels = [l for l in labels if l.get("type") == "user"]
        
        if system_labels:
            print("📧 System Labels:")
            for label in sorted(system_labels, key=lambda x: x.get("name", "")):
                name = label.get("name", "Unknown")
                print(f"   • {name}")
        
        if user_labels:
            print(f"\n🏷️  User Labels ({len(user_labels)}):")
            for label in sorted(user_labels, key=lambda x: x.get("name", "")):
                name = label.get("name", "Unknown")
                print(f"   • {name}")
        
        print(f"\n🎉 Successfully listed {len(labels)} Gmail labels!")
        
    except Exception as e:
        print(f"❌ Error listing labels: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

