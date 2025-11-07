# Storage Management and Backup Retention

This guide explains how to manage storage capacity and implement backup retention policies for Gmail backups.

## Overview

As backups accumulate over time, storage management becomes critical. This guide covers:
- Storage capacity planning
- Backup retention policies
- Automated cleanup procedures
- Storage monitoring

## Storage Capacity Planning

### Estimating Storage Requirements

**Average Email Size:**
- Typical email: 10-50 KB
- Email with attachments: 100 KB - 5 MB
- Average across mailbox: ~30 KB per email

**Storage Calculation:**
```
Daily emails × Average size × Retention period = Required storage

Example:
- 50 emails/day × 30 KB = 1.5 MB/day
- 1.5 MB/day × 30 days = 45 MB/month
- 1.5 MB/day × 365 days = 547 MB/year
```

**Full Backup Size:**
- Small mailbox (< 1,000 emails): ~30-50 MB
- Medium mailbox (1,000-10,000 emails): ~300-500 MB
- Large mailbox (10,000+ emails): ~3-5 GB+

### Recommended Storage Allocation

**Minimum Requirements:**
- **Daily incremental backups**: 50-100 MB
- **Weekly full backups**: 500 MB - 2 GB
- **Monthly retention**: 2-5 GB
- **Yearly retention**: 10-20 GB

**Recommended Allocation:**
- **Local storage**: 10-20 GB for recent backups
- **Cloud/external storage**: 50-100 GB for long-term retention
- **Total capacity**: 50-100 GB for comprehensive backup strategy

## Backup Retention Policies

### Policy Options

**1. Time-Based Retention**
- Keep backups newer than N days
- Example: Keep all backups from last 30 days

**2. Count-Based Retention**
- Keep last N backups
- Example: Keep last 10 backups regardless of age

**3. Hybrid Retention (Recommended)**
- Keep last N backups OR backups newer than M days
- Example: Keep last 20 backups OR backups newer than 60 days

### Recommended Policies

**For Daily Incremental Backups:**
```bash
# Keep last 30 days of incremental backups
--keep-days 30
```

**For Weekly Full Backups:**
```bash
# Keep last 12 full backups (3 months)
--keep-count 12
```

**Combined Strategy:**
```bash
# Keep last 20 backups OR backups newer than 60 days
--keep-count 20 --keep-days 60
```

## Automated Cleanup

### Using Cleanup Script

The cleanup script (`scripts/cleanup_backups.py`) manages backup retention:

**Dry Run (Preview):**
```bash
# Activate virtual environment first (if using venv)
source .venv/bin/activate

# See what would be deleted without actually deleting
python scripts/cleanup_backups.py --keep-days 30 --dry-run
```

**Delete Old Backups:**
```bash
# Activate virtual environment first (if using venv)
source .venv/bin/activate

# Delete backups older than 30 days
python scripts/cleanup_backups.py --keep-days 30

# Keep only last 10 backups
python scripts/cleanup_backups.py --keep-count 10

# Combined: Keep last 20 OR backups newer than 60 days
python scripts/cleanup_backups.py --keep-count 20 --keep-days 60
```

### Integration with Cron

Add cleanup to your backup schedule:

**Daily cleanup after backup:**
```cron
# Daily backup at 2 AM, cleanup at 2:30 AM
0 2 * * * /path/to/scripts/run_backup.sh
30 2 * * * /path/to/scripts/cleanup_backups.py --keep-days 30
```

**Weekly cleanup:**
```cron
# Weekly cleanup on Sunday at 4 AM
0 4 * * 0 /path/to/scripts/cleanup_backups.py --keep-count 20 --keep-days 60
```

## Storage Monitoring

### Check Current Storage Usage

**View backup folder size:**
```bash
# Total size of backup folder
du -sh backups/gmail

# Size of individual backup files
du -h backups/gmail/*.mbox | sort -h

# Count of backup files
find backups/gmail -name "*.mbox" -type f | wc -l
```

### Monitor Disk Space

**Check available disk space:**
```bash
# macOS/Linux
df -h backups/gmail

# Windows
dir backups\gmail
```

**Set up disk space alerts:**
```bash
# Alert if disk usage exceeds 80%
df -h | awk '$5 > 80 {print "Warning: Disk usage at", $5}'
```

### Storage Status Script

Create a monitoring script:

**`scripts/check_storage.py`:**
```python
#!/usr/bin/env python3
"""Check backup storage status."""

from pathlib import Path
from datetime import datetime

backup_folder = Path("backups/gmail")
backup_files = list(backup_folder.glob("*.mbox"))

total_size = sum(f.stat().st_size for f in backup_files)
total_size_mb = total_size / (1024 * 1024)

print(f"📦 Backup Storage Status")
print(f"   Files: {len(backup_files)}")
print(f"   Total size: {total_size_mb:.1f} MB")

# Check disk space
import shutil
total, used, free = shutil.disk_usage(backup_folder)
free_gb = free / (1024 ** 3)
used_percent = (used / total) * 100

print(f"\n💾 Disk Space")
print(f"   Free: {free_gb:.1f} GB")
print(f"   Used: {used_percent:.1f}%")

if used_percent > 80:
    print("   ⚠️  Warning: Disk usage above 80%")
```

## Backup Folder Structure

### Recommended Structure

```
backups/
├── gmail/
│   ├── backup_state.json          # Backup state tracking
│   ├── gmail_backup_incremental_20251106_020000.mbox
│   ├── gmail_backup_incremental_20251107_020000.mbox
│   ├── gmail_backup_full_20251101_030000.mbox
│   └── ...
└── archive/                        # Optional: Archived backups
    └── gmail/
        └── 2025-11/
            └── ...
```

### Backup Naming Convention

Backups use timestamp-based naming:
```
gmail_backup_{type}_{timestamp}.mbox

Examples:
- gmail_backup_incremental_20251106_020000.mbox
- gmail_backup_full_20251101_030000.mbox
```

## Configuration

### Retention Settings in Config

Edit `config/config.json`:

```json
{
  "services": {
    "gmail": {
      "backup_folder": "backups/gmail",
      "max_messages_per_backup": 1000
    }
  },
  "backup": {
    "retention_days": 30,
    "retention_count": 10,
    "cleanup_enabled": true,
    "cleanup_schedule": "0 3 * * *"
  }
}
```

### Environment Variables

```bash
# Retention policy
export BACKUP_RETENTION_DAYS=30
export BACKUP_RETENTION_COUNT=10

# Backup folder
export MCP_GMAIL__BACKUP_FOLDER="backups/gmail"
```

## Best Practices

### 1. Regular Cleanup

- **Daily**: Cleanup old incremental backups (keep 30 days)
- **Weekly**: Cleanup old full backups (keep last 12)
- **Monthly**: Review and archive important backups

### 2. Storage Monitoring

- Monitor disk usage weekly
- Set up alerts for low disk space (< 20% free)
- Track backup growth trends

### 3. Retention Strategy

- **Short-term**: Keep daily incremental backups for 30 days
- **Medium-term**: Keep weekly full backups for 3 months
- **Long-term**: Archive monthly full backups to external storage

### 4. Backup Verification

- Verify backups after cleanup
- Test restore from retained backups
- Document retention policy and schedule

### 5. Storage Expansion

**When to expand storage:**
- Disk usage consistently > 80%
- Backup growth rate exceeds available space
- Need to extend retention period

**Options:**
- External drive for archive backups
- Cloud storage (Google Drive, Dropbox, etc.)
- Network-attached storage (NAS)
- Cloud backup service

## Troubleshooting

### Issue: Disk Space Running Low

**Solutions:**
- Run cleanup script immediately: `python scripts/cleanup_backups.py --keep-days 7`
- Move old backups to external storage
- Reduce retention period temporarily
- Compress old backups (if supported)

### Issue: Cleanup Not Running

**Solutions:**
- Check cron job is configured correctly
- Verify script has execute permissions: `chmod +x scripts/cleanup_backups.py`
- Test script manually: `python scripts/cleanup_backups.py --dry-run`
- Check cron logs for errors

### Issue: Important Backup Deleted

**Solutions:**
- Use `--dry-run` before cleanup to preview deletions
- Archive important backups before cleanup
- Adjust retention policy to keep more backups
- Restore from external/cloud backup if available

## Example Complete Setup

**1. Configure retention in config:**
```json
{
  "backup": {
    "retention_days": 30,
    "retention_count": 20
  }
}
```

**2. Add cleanup to cron:**
```cron
# Daily cleanup at 3 AM (after backup at 2 AM)
0 3 * * * /path/to/mcp-google-services/scripts/cleanup_backups.py --keep-days 30 --keep-count 20
```

**3. Monitor storage:**
```bash
# Weekly storage check
0 9 * * 1 /path/to/mcp-google-services/scripts/check_storage.py
```

## Related Documentation

- [Scheduling Guide](SCHEDULING_GUIDE.md) - Automated backup scheduling
- [Backup System](services/BACKUP_SYSTEM.md) - Backup operations explained
- [Restore Guide](RESTORE_GUIDE.md) - Restoring from backups
- [Troubleshooting Guide](TROUBLESHOOTING.md) - Common issues and solutions

---

**Last Updated**: November 2025  
**MCP Server Version**: 1.0.0

