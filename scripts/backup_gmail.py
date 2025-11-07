#!/usr/bin/env python3
"""Standalone Gmail backup script for automated scheduling.

This script can be run directly or via cron for automated Gmail backups.
It uses the Google MCP server's backup functionality.

Usage:
    python scripts/backup_gmail.py [--type incremental|full] [--max-results N] [--query QUERY]
    
Environment Variables:
    GOOGLE_APPLICATION_CREDENTIALS: Path to OAuth credentials file
    MCP_GMAIL__BACKUP_FOLDER: Backup folder path (default: backups/gmail)
    MCP_GMAIL__MAX_MESSAGES_PER_BACKUP: Max messages per backup (default: 1000)
"""

import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mcp_google_services.utils.config import Config
from mcp_google_services.core.auth import AuthManager
from mcp_google_services.services.gmail.api import GmailAPI
from mcp_google_services.services.gmail.backup import GmailBackup


def main():
    """Main backup execution."""
    parser = argparse.ArgumentParser(
        description="Automated Gmail backup script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Incremental backup (default)
  python scripts/backup_gmail.py
  
  # Full backup
  python scripts/backup_gmail.py --type full
  
  # Backup with custom query
  python scripts/backup_gmail.py --query "from:important@example.com"
  
  # Limit number of messages
  python scripts/backup_gmail.py --max-results 500
        """
    )
    
    parser.add_argument(
        "--type",
        choices=["incremental", "full"],
        default="incremental",
        help="Backup type: incremental (default) or full"
    )
    
    parser.add_argument(
        "--max-results",
        type=int,
        default=None,
        help="Maximum number of messages to backup"
    )
    
    parser.add_argument(
        "--query",
        type=str,
        default=None,
        help="Gmail search query to filter messages"
    )
    
    parser.add_argument(
        "--user-id",
        type=str,
        default="me",
        help="Gmail user ID (default: 'me')"
    )
    
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to config.json file"
    )
    
    args = parser.parse_args()
    
    # Initialize configuration
    config_path = Path(args.config) if args.config else None
    config = Config(config_path=config_path)
    
    # Authenticate
    print("🔐 Authenticating...")
    try:
        auth_manager = AuthManager(config=config)
        credentials = auth_manager.get_credentials(args.user_id)
        print("✅ Authentication successful")
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        sys.exit(1)
    
    # Initialize Gmail API and backup service
    print("📧 Initializing Gmail backup service...")
    gmail_api = GmailAPI(credentials=credentials)
    backup_service = GmailBackup(api=gmail_api, config=config)
    
    # Execute backup
    print(f"🔄 Starting {args.type} backup...")
    try:
        if args.type == "incremental":
            result = backup_service.incremental_backup(
                user_id=args.user_id,
                query=args.query,
                max_results=args.max_results
            )
        else:
            result = backup_service.full_backup(
                user_id=args.user_id,
                query=args.query,
                max_results=args.max_results
            )
        
        if result.success:
            duration = (result.end_time - result.start_time).total_seconds()
            print(f"\n✅ Backup completed successfully!")
            print(f"   Messages backed up: {result.message_count}")
            print(f"   Messages processed: {result.messages_processed}")
            print(f"   Messages failed: {result.messages_failed}")
            print(f"   Backup path: {result.backup_path}")
            print(f"   Duration: {duration:.1f} seconds")
            sys.exit(0)
        else:
            print(f"\n❌ Backup failed: {result.error}")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Backup error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

