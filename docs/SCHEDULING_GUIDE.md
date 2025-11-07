# Automated Backup Scheduling Guide

This guide explains how to set up automated Gmail backups using the Google Services MCP Server.

## Overview

Automated backups can be configured using:
1. **System Cron Jobs** (Recommended) - Use system-level cron for reliable scheduling
2. **Configuration-Based Scheduling** - Use scheduler configuration (when fully implemented)

## Prerequisites

- Google MCP server installed and configured
- OAuth credentials configured (`config/credentials.json`)
- Backup script executable: `scripts/backup_gmail.py`

## System Cron Scheduling (Recommended)

### Step 1: Create Backup Script Wrapper

Create a wrapper script that sets up the environment:

**macOS/Linux: `scripts/run_backup.sh`**
```bash
#!/bin/bash
# Gmail backup wrapper script for cron

# Set working directory
cd /path/to/mcp-google-services

# Activate virtual environment (if using venv)
source .venv/bin/activate

# Set environment variables
export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/config/credentials.json"
export PYTHONPATH="$(pwd)/src"

# Run backup
python scripts/backup_gmail.py --type incremental >> logs/backup.log 2>&1
```

Make it executable:
```bash
chmod +x scripts/run_backup.sh
```

### Step 2: Configure Cron Job

#### macOS/Linux

Edit crontab:
```bash
crontab -e
```

Add backup schedule:

**Daily at 2 AM (Incremental):**
```cron
0 2 * * * /path/to/mcp-google-services/scripts/run_backup.sh
```

**Weekly Full Backup (Sunday at 3 AM) + Daily Incremental:**
```cron
# Daily incremental backup at 2 AM
0 2 * * * /path/to/mcp-google-services/scripts/run_backup.sh --type incremental

# Weekly full backup on Sunday at 3 AM
0 3 * * 0 /path/to/mcp-google-services/scripts/run_backup.sh --type full
```

**Multiple Times Per Day:**
```cron
# Every 6 hours
0 */6 * * * /path/to/mcp-google-services/scripts/run_backup.sh
```

#### Windows (Task Scheduler)

1. Open **Task Scheduler**
2. Create **Basic Task**
3. Set trigger (e.g., Daily at 2:00 AM)
4. Set action: **Start a program**
   - Program: `python`
   - Arguments: `C:\path\to\mcp-google-services\scripts\backup_gmail.py --type incremental`
   - Start in: `C:\path\to\mcp-google-services`
5. Configure environment variables in task settings

### Step 3: Verify Cron Job

**Check cron logs:**
```bash
# macOS
grep CRON /var/log/system.log

# Linux
grep CRON /var/log/syslog
```

**Test manually:**
```bash
/path/to/mcp-google-services/scripts/run_backup.sh
```

## Common Cron Schedule Examples

### Daily Backups

```cron
# Daily at 2 AM
0 2 * * * /path/to/scripts/run_backup.sh

# Daily at midnight
0 0 * * * /path/to/scripts/run_backup.sh

# Twice daily (2 AM and 2 PM)
0 2,14 * * * /path/to/scripts/run_backup.sh
```

### Weekly Backups

```cron
# Every Monday at 2 AM
0 2 * * 1 /path/to/scripts/run_backup.sh

# Every Sunday at 3 AM
0 3 * * 0 /path/to/scripts/run_backup.sh
```

### Monthly Backups

```cron
# First day of month at 2 AM
0 2 1 * * /path/to/scripts/run_backup.sh
```

### Combined Strategy (Recommended)

**Incremental Daily + Full Weekly:**
```cron
# Daily incremental at 2 AM
0 2 * * * /path/to/scripts/run_backup.sh --type incremental

# Weekly full backup on Sunday at 3 AM
0 3 * * 0 /path/to/scripts/run_backup.sh --type full --max-results 10000
```

## Configuration-Based Scheduling

### Step 1: Enable Scheduling in Config

Edit `config/config.json`:

```json
{
  "schedule": {
    "enabled": true,
    "default_cron": "0 2 * * *",
    "timezone": "UTC",
    "services": {
      "gmail": "0 2 * * *"
    }
  },
  "services": {
    "gmail": {
      "backup_folder": "backups/gmail",
      "max_messages_per_backup": 1000
    }
  }
}
```

### Step 2: Cron Expression Format

Cron expressions use standard format:
```
* * * * *
│ │ │ │ │
│ │ │ │ └─── Day of week (0-7, 0 or 7 = Sunday)
│ │ │ └───── Month (1-12)
│ │ └─────── Day of month (1-31)
│ └───────── Hour (0-23)
└─────────── Minute (0-59)
```

**Common Examples:**
- `0 2 * * *` - Daily at 2:00 AM
- `0 */6 * * *` - Every 6 hours
- `0 2 * * 0` - Every Sunday at 2:00 AM
- `0 0 1 * *` - First day of month at midnight
- `0 2,14 * * *` - Daily at 2:00 AM and 2:00 PM

## Monitoring and Notifications

### Log File Monitoring

Backup script outputs to logs. Monitor with:

```bash
# View recent backups
tail -f logs/backup.log

# Check for errors
grep -i error logs/backup.log

# Check backup success
grep "Backup completed successfully" logs/backup.log
```

### Email Notifications

Add email notification to backup script:

**Enhanced `scripts/run_backup.sh`:**
```bash
#!/bin/bash
cd /path/to/mcp-google-services
source .venv/bin/activate
export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/config/credentials.json"
export PYTHONPATH="$(pwd)/src"

# Run backup and capture output
OUTPUT=$(python scripts/backup_gmail.py --type incremental 2>&1)
EXIT_CODE=$?

# Send email notification on failure
if [ $EXIT_CODE -ne 0 ]; then
    echo "$OUTPUT" | mail -s "Gmail Backup Failed" your-email@example.com
fi

# Log output
echo "$(date): $OUTPUT" >> logs/backup.log
```

### Backup Status Check

Create status check script:

**`scripts/check_backup_status.py`:**
```python
#!/usr/bin/env python3
"""Check backup status and send alerts if needed."""

import json
from pathlib import Path
from datetime import datetime, timedelta

backup_state_file = Path("backups/gmail/backup_state.json")

if not backup_state_file.exists():
    print("❌ No backup state found - backups may not be running")
    exit(1)

with open(backup_state_file) as f:
    state = json.load(f)

for user_id, user_state in state.items():
    last_backup_str = user_state.get("last_backup_time")
    if last_backup_str:
        last_backup = datetime.fromisoformat(last_backup_str)
        hours_since = (datetime.now() - last_backup).total_seconds() / 3600
        
        if hours_since > 48:  # Alert if no backup in 48 hours
            print(f"⚠️  Warning: Last backup for {user_id} was {hours_since:.1f} hours ago")
        else:
            print(f"✅ Last backup for {user_id}: {hours_since:.1f} hours ago")
```

## Troubleshooting

### Issue: Cron Job Not Running

**Solutions:**
- Check cron service is running: `systemctl status cron` (Linux)
- Verify cron job syntax: `crontab -l`
- Check cron logs for errors
- Ensure script has execute permissions: `chmod +x scripts/run_backup.sh`
- Use absolute paths in cron (cron doesn't use your shell environment)

### Issue: Authentication Fails in Cron

**Solutions:**
- Ensure `GOOGLE_APPLICATION_CREDENTIALS` environment variable is set in cron
- Use absolute path to credentials file
- Check file permissions on credentials file
- Test script manually first: `./scripts/run_backup.sh`

### Issue: Python Not Found in Cron

**Solutions:**
- Use full path to Python: `/usr/bin/python3` or `/path/to/venv/bin/python`
- Or activate virtual environment in script wrapper
- Check `which python3` to find correct path

### Issue: Backup Script Fails Silently

**Solutions:**
- Redirect output to log file: `>> logs/backup.log 2>&1`
- Check log file for errors
- Test script manually to see error messages
- Add error handling and email notifications

## Best Practices

1. **Start with Manual Testing**: Test backup script manually before setting up cron
2. **Use Incremental Backups**: Use incremental for daily, full for weekly/monthly
3. **Monitor Logs**: Regularly check backup logs for errors
4. **Set Up Alerts**: Configure email notifications for backup failures
5. **Test Restore**: Periodically test restore from backups to verify integrity
6. **Backup Retention**: Implement retention policy to manage disk space
7. **Document Schedule**: Document your backup schedule and retention policy

## Example Complete Setup

**1. Create wrapper script: `scripts/run_backup.sh`**
```bash
#!/bin/bash
cd /Users/username/git/github/CloudBoostUP/mcp-google-services
source .venv/bin/activate
export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/config/credentials.json"
export PYTHONPATH="$(pwd)/src"
python scripts/backup_gmail.py --type incremental >> logs/backup.log 2>&1
```

**2. Add to crontab:**
```cron
# Daily incremental backup at 2 AM
0 2 * * * /Users/username/git/github/CloudBoostUP/mcp-google-services/scripts/run_backup.sh

# Weekly full backup on Sunday at 3 AM
0 3 * * 0 /Users/username/git/github/CloudBoostUP/mcp-google-services/scripts/run_backup.sh --type full
```

**3. Verify:**
```bash
# Check cron is set up
crontab -l

# Test manually
./scripts/run_backup.sh

# Check logs
tail -f logs/backup.log
```

## Related Documentation

- [Backup System](BACKUP_SYSTEM.md) - Incremental vs full backup explained
- [Restore Guide](RESTORE_GUIDE.md) - How to restore from backups
- [Troubleshooting Guide](TROUBLESHOOTING.md) - Common issues and solutions
- [Configuration Guide](../README.md#configuration) - Configuration options

---

**Last Updated**: November 2025  
**MCP Server Version**: 1.0.0

