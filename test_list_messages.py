#!/usr/bin/env python3
"""Test script to list Gmail messages."""

import sys
from pathlib import Path
from datetime import datetime

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
    
    print("\n📧 Fetching Gmail messages...")
    gmail_api = GmailAPI(credentials=credentials)
    
    try:
        # List recent messages (max 10 for testing)
        result = gmail_api.list_messages(user_id="me", max_results=10)
        messages = result.get("messages", [])
        
        if not messages:
            print("\n📭 No messages found in your inbox.")
            return
        
        print(f"\n✅ Found {len(messages)} recent messages:\n")
        
        # Get full message details for each
        for i, msg_summary in enumerate(messages, 1):
            msg_id = msg_summary.get("id")
            print(f"\n{i}. Message ID: {msg_id}")
            
            # Get full message details
            try:
                full_message = gmail_api.get_message(user_id="me", message_id=msg_id, format="metadata")
                
                # Extract headers
                headers = {}
                payload = full_message.get("payload", {})
                for header in payload.get("headers", []):
                    name = header.get("name", "").lower()
                    value = header.get("value", "")
                    headers[name] = value
                
                subject = headers.get("subject", "(No subject)")
                from_addr = headers.get("from", "Unknown")
                date_str = headers.get("date", "")
                
                # Parse date if available
                date_display = date_str
                try:
                    from email.utils import parsedate_to_datetime
                    if date_str:
                        date_obj = parsedate_to_datetime(date_str)
                        date_display = date_obj.strftime("%Y-%m-%d %H:%M")
                except:
                    pass
                
                snippet = full_message.get("snippet", "")
                labels = full_message.get("labelIds", [])
                
                print(f"   Subject: {subject[:60]}{'...' if len(subject) > 60 else ''}")
                print(f"   From: {from_addr[:50]}{'...' if len(from_addr) > 50 else ''}")
                print(f"   Date: {date_display}")
                print(f"   Labels: {', '.join(labels[:5])}{'...' if len(labels) > 5 else ''}")
                print(f"   Snippet: {snippet[:80]}{'...' if len(snippet) > 80 else ''}")
                
            except Exception as e:
                print(f"   ⚠️  Could not fetch full details: {e}")
                print(f"   Thread ID: {msg_summary.get('threadId', 'N/A')}")
        
        print(f"\n🎉 Successfully listed {len(messages)} Gmail messages!")
        print(f"\n💡 Tip: Use 'max_results' parameter to get more messages.")
        
    except Exception as e:
        print(f"❌ Error listing messages: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

