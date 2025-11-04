#!/usr/bin/env python3
"""Debug version of backup test."""

import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

sys.path.insert(0, str(Path(__file__).parent / "src"))

from mcp_google_services.utils.config import Config
from mcp_google_services.core.auth import AuthManager
from mcp_google_services.services.gmail.api import GmailAPI
from mcp_google_services.services.gmail.backup import GmailBackup

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
    
    print("\n📧 Testing Gmail API...")
    gmail_api = GmailAPI(credentials=credentials)
    
    # First, list messages
    print("Listing messages...")
    result = gmail_api.list_messages(user_id="me", max_results=5)
    messages = result.get("messages", [])
    print(f"Found {len(messages)} messages")
    
    if not messages:
        print("No messages to backup!")
        return
    
    # Get one message to test parsing
    print(f"\nTesting message parsing with message ID: {messages[0]['id']}")
    try:
        full_message = gmail_api.get_message(user_id="me", message_id=messages[0]['id'], format="full")
        print(f"✅ Got full message: {full_message.keys()}")
        
        from mcp_google_services.services.gmail.parser import EmailParser
        parser = EmailParser()
        parsed = parser.parse_message(full_message)
        print(f"✅ Parsed message: {list(parsed.keys())}")
        print(f"   From: {parsed.get('from', 'N/A')}")
        print(f"   Subject: {parsed.get('subject', 'N/A')[:50]}")
        
        # Test MBOX generation
        from mcp_google_services.services.gmail.mbox import MBOXGenerator
        test_path = Path("backups/gmail/test_backup.mbox")
        test_path.parent.mkdir(parents=True, exist_ok=True)
        
        with MBOXGenerator(str(test_path)) as mbox:
            mbox.add_message(parsed)
            print(f"✅ Added message to MBOX: {test_path}")
            print(f"   Message count: {mbox.message_count}")
        
        if test_path.exists():
            size = test_path.stat().st_size
            print(f"✅ MBOX file created: {size} bytes")
            test_path.unlink()  # Clean up
        else:
            print("❌ MBOX file not created!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

