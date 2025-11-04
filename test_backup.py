#!/usr/bin/env python3
"""Test script to backup Gmail messages."""

import sys
from pathlib import Path
from datetime import datetime

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
    
    print("\n📧 Starting Gmail backup...")
    gmail_api = GmailAPI(credentials=credentials)
    backup_service = GmailBackup(api=gmail_api, config=config)
    
    try:
        # Perform incremental backup (first run will be full backup)
        print("Performing incremental backup (first run will back up all messages)...")
        print("This may take a moment...\n")
        
        result = backup_service.incremental_backup(
            user_id="me",
            max_results=20  # Limit to 20 messages for testing
        )
        
        if result.success:
            print("✅ Backup completed successfully!\n")
            print(f"📊 Summary:")
            print(f"   • Messages backed up: {result.message_count}")
            print(f"   • Messages processed: {result.messages_processed}")
            print(f"   • Messages failed: {result.messages_failed}")
            
            if result.end_time:
                duration = (result.end_time - result.start_time).total_seconds()
                print(f"   • Duration: {duration:.2f} seconds")
            
            print(f"\n💾 Backup saved to:")
            print(f"   {result.backup_path}")
            
            # Check file size
            backup_file = Path(result.backup_path)
            if backup_file.exists():
                file_size = backup_file.stat().st_size
                print(f"\n📦 File size: {file_size:,} bytes ({file_size / 1024:.2f} KB)")
            
            print(f"\n🎉 Backup successful!")
            print(f"\n💡 Tip: Next backup will only include new messages since this backup.")
        else:
            print(f"❌ Backup failed: {result.error}")
            
    except Exception as e:
        print(f"❌ Error during backup: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

