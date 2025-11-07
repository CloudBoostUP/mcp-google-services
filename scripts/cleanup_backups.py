#!/usr/bin/env python3
"""Backup cleanup script for managing backup retention.

This script implements backup retention policies to manage disk space
by removing old backup files based on configurable retention rules.

Usage:
    python scripts/cleanup_backups.py [--keep-days N] [--keep-count N] [--dry-run]
    
Environment Variables:
    MCP_GMAIL__BACKUP_FOLDER: Backup folder path (default: backups/gmail)
    BACKUP_RETENTION_DAYS: Keep backups newer than N days (default: 30)
    BACKUP_RETENTION_COUNT: Keep last N backups (default: 10)
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Tuple

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mcp_google_services.utils.config import Config


def get_backup_files(backup_folder: Path) -> List[Tuple[Path, datetime]]:
    """Get all backup files with their modification times.
    
    Args:
        backup_folder: Path to backup folder
        
    Returns:
        List of tuples (file_path, modification_time) sorted by time (oldest first)
    """
    backup_files = []
    
    if not backup_folder.exists():
        return backup_files
    
    for file_path in backup_folder.glob("*.mbox"):
        if file_path.is_file():
            mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
            backup_files.append((file_path, mtime))
    
    # Sort by modification time (oldest first)
    backup_files.sort(key=lambda x: x[1])
    return backup_files


def cleanup_by_days(backup_folder: Path, keep_days: int, dry_run: bool = False) -> Tuple[int, int]:
    """Remove backups older than specified days.
    
    Args:
        backup_folder: Path to backup folder
        keep_days: Keep backups newer than this many days
        dry_run: If True, only report what would be deleted
        
    Returns:
        Tuple of (files_deleted, space_freed_bytes)
    """
    cutoff_date = datetime.now() - timedelta(days=keep_days)
    backup_files = get_backup_files(backup_folder)
    
    files_deleted = 0
    space_freed = 0
    
    for file_path, mtime in backup_files:
        if mtime < cutoff_date:
            file_size = file_path.stat().st_size
            if dry_run:
                print(f"Would delete: {file_path.name} ({file_size:,} bytes, {mtime.strftime('%Y-%m-%d %H:%M:%S')})")
            else:
                try:
                    file_path.unlink()
                    print(f"Deleted: {file_path.name} ({file_size:,} bytes)")
                    files_deleted += 1
                    space_freed += file_size
                except Exception as e:
                    print(f"Error deleting {file_path.name}: {e}")
    
    return files_deleted, space_freed


def cleanup_by_count(backup_folder: Path, keep_count: int, dry_run: bool = False) -> Tuple[int, int]:
    """Keep only the most recent N backups.
    
    Args:
        backup_folder: Path to backup folder
        keep_count: Number of most recent backups to keep
        dry_run: If True, only report what would be deleted
        
    Returns:
        Tuple of (files_deleted, space_freed_bytes)
    """
    backup_files = get_backup_files(backup_folder)
    
    if len(backup_files) <= keep_count:
        if dry_run:
            print(f"Would keep all {len(backup_files)} backups (limit: {keep_count})")
        return 0, 0
    
    # Files to delete (all except the last keep_count)
    files_to_delete = backup_files[:-keep_count]
    
    files_deleted = 0
    space_freed = 0
    
    for file_path, mtime in files_to_delete:
        file_size = file_path.stat().st_size
        if dry_run:
            print(f"Would delete: {file_path.name} ({file_size:,} bytes, {mtime.strftime('%Y-%m-%d %H:%M:%S')})")
        else:
            try:
                file_path.unlink()
                print(f"Deleted: {file_path.name} ({file_size:,} bytes)")
                files_deleted += 1
                space_freed += file_size
            except Exception as e:
                print(f"Error deleting {file_path.name}: {e}")
    
    return files_deleted, space_freed


def format_bytes(bytes_value: int) -> str:
    """Format bytes to human-readable string.
    
    Args:
        bytes_value: Size in bytes
        
    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} PB"


def main():
    """Main cleanup execution."""
    parser = argparse.ArgumentParser(
        description="Cleanup old Gmail backup files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run: See what would be deleted (keep backups newer than 30 days)
  python scripts/cleanup_backups.py --keep-days 30 --dry-run
  
  # Delete backups older than 30 days
  python scripts/cleanup_backups.py --keep-days 30
  
  # Keep only last 10 backups
  python scripts/cleanup_backups.py --keep-count 10
  
  # Combined: Keep last 20 OR backups newer than 60 days
  python scripts/cleanup_backups.py --keep-count 20 --keep-days 60
        """
    )
    
    parser.add_argument(
        "--keep-days",
        type=int,
        default=None,
        help="Keep backups newer than N days (default: from config or 30)"
    )
    
    parser.add_argument(
        "--keep-count",
        type=int,
        default=None,
        help="Keep last N backups (default: from config or 10)"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be deleted without actually deleting"
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
    
    # Get backup folder
    backup_folder = Path(config.get("gmail.backup_folder", "backups/gmail"))
    backup_folder.mkdir(parents=True, exist_ok=True)
    
    # Get retention settings
    keep_days = args.keep_days or config.get("backup.retention_days", 30)
    keep_count = args.keep_count or config.get("backup.retention_count", 10)
    
    print(f"📁 Backup folder: {backup_folder}")
    print(f"📊 Retention policy:")
    if args.keep_days or config.get("backup.retention_days"):
        print(f"   - Keep backups newer than {keep_days} days")
    if args.keep_count or config.get("backup.retention_count"):
        print(f"   - Keep last {keep_count} backups")
    print(f"   - Mode: {'DRY RUN' if args.dry_run else 'DELETE'}")
    print()
    
    # Get current backup files
    backup_files = get_backup_files(backup_folder)
    total_size = sum(f.stat().st_size for f, _ in backup_files)
    
    print(f"📦 Current backups: {len(backup_files)} files, {format_bytes(total_size)}")
    print()
    
    # Apply retention policies
    files_deleted = 0
    space_freed = 0
    
    if keep_days:
        deleted, freed = cleanup_by_days(backup_folder, keep_days, args.dry_run)
        files_deleted += deleted
        space_freed += freed
    
    if keep_count:
        deleted, freed = cleanup_by_count(backup_folder, keep_count, args.dry_run)
        files_deleted += deleted
        space_freed += freed
    
    print()
    if args.dry_run:
        print(f"📋 Would delete: {files_deleted} files, {format_bytes(space_freed)}")
    else:
        print(f"✅ Cleanup complete: {files_deleted} files deleted, {format_bytes(space_freed)} freed")
        
        # Show remaining backups
        remaining = get_backup_files(backup_folder)
        remaining_size = sum(f.stat().st_size for f, _ in remaining)
        print(f"📦 Remaining backups: {len(remaining)} files, {format_bytes(remaining_size)}")


if __name__ == "__main__":
    main()

