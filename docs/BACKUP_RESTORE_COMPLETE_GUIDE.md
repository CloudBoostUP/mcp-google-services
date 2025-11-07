# Complete Gmail Backup and Restore Guide

This comprehensive guide covers the complete workflow for automated Gmail backup and restore using the Google Services MCP Server.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Initial Setup](#initial-setup)
3. [Backup Operations](#backup-operations)
4. [Automated Scheduling](#automated-scheduling)
5. [Storage Management](#storage-management)
6. [Restore Procedures](#restore-procedures)
7. [Maintenance](#maintenance)
8. [Troubleshooting](#troubleshooting)

## Quick Start

### 5-Minute Setup

1. **Install and Configure MCP Server**
   ```bash
   cd mcp-google-services
   pip install -r requirements.txt
   # Place OAuth credentials in config/credentials.json
   ```

2. **Test Backup**
   ```bash
   python scripts/backup_gmail.py --type incremental --max-results 10
   ```

3. **Set Up Automated Scheduling**
   ```bash
   # Copy wrapper script
   cp scripts/run_backup.sh.example scripts/run_backup.sh
   # Edit paths in run_backup.sh
   # Add to crontab: 0 2 * * * /path/to/scripts/run_backup.sh
   ```

4. **Verify Restore**
   - Import MBOX file into Thunderbird or Apple Mail
   - Verify emails are accessible

## Initial Setup

### Prerequisites

- Python 3.8 or higher
- Google Cloud Project with Gmail API enabled
- OAuth 2.0 credentials file
- Virtual environment (recommended)

### Step 1: Install Dependencies

```bash
cd mcp-google-services
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2: Configure Google API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create or select a project
3. Enable **Gmail API**:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Gmail API"
   - Click "Enable"
4. Create OAuth 2.0 Credentials:
   - Navigate to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Desktop app" as application type
   - Download the JSON file
5. Place credentials in `config/credentials.json`

### Step 3: Configure MCP Server in Cursor

Add to `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "google-services": {
      "command": "/path/to/mcp-google-services/.venv/bin/python",
      "args": ["-m", "mcp_google_services.server"],
      "env": {
        "PYTHONPATH": "/path/to/mcp-google-services/src"
      }
    }
  }
}
```

Restart Cursor to load the MCP server.

### Step 4: Test Authentication

```bash
# Test authentication
python scripts/backup_gmail.py --type incremental --max-results 5
```

First run will open browser for OAuth consent. After approval, credentials are stored securely.

## Backup Operations

### Manual Backup

**Using MCP Tools in Cursor:**
```
"Backup my Gmail messages"
"Create a full backup of my Gmail"
"Do an incremental backup of my emails"
```

**Using Command Line:**
```bash
# Incremental backup (recommended for regular use)
python scripts/backup_gmail.py --type incremental

# Full backup (for complete mailbox backup)
python scripts/backup_gmail.py --type full

# Backup with custom query
python scripts/backup_gmail.py --query "from:important@example.com"

# Limit number of messages
python scripts/backup_gmail.py --max-results 500
```

### Backup Types

**Incremental Backup:**
- Only backs up new messages since last backup
- Faster and more efficient
- Recommended for daily/weekly scheduled backups
- Uses `backup_state.json` to track last backup time

**Full Backup:**
- Backs up all messages matching criteria
- Complete mailbox snapshot
- Recommended for monthly/quarterly backups
- Independent of previous backups

### Backup Output

Backups are saved as MBOX files:
```
backups/gmail/gmail_backup_incremental_20251106_020000.mbox
backups/gmail/gmail_backup_full_20251101_030000.mbox
```

**Backup State Tracking:**
- State stored in `backups/gmail/backup_state.json`
- Tracks last backup time per user
- Enables incremental backup functionality

## Automated Scheduling

### Recommended Schedule

**Daily Incremental + Weekly Full:**
```cron
# Daily incremental backup at 2 AM
0 2 * * * /path/to/mcp-google-services/scripts/run_backup.sh --type incremental

# Weekly full backup on Sunday at 3 AM
0 3 * * 0 /path/to/mcp-google-services/scripts/run_backup.sh --type full
```

### Setup Steps

1. **Create Wrapper Script**
   ```bash
   cp scripts/run_backup.sh.example scripts/run_backup.sh
   # Edit paths in run_backup.sh
   chmod +x scripts/run_backup.sh
   ```

2. **Configure Cron**
   ```bash
   crontab -e
   # Add backup schedule
   ```

3. **Test Manually**
   ```bash
   ./scripts/run_backup.sh
   tail -f logs/backup.log
   ```

4. **Monitor**
   - Check logs regularly: `tail -f logs/backup.log`
   - Verify backups are created: `ls -lh backups/gmail/`
   - Check backup state: `cat backups/gmail/backup_state.json`

For detailed scheduling setup, see [Scheduling Guide](SCHEDULING_GUIDE.md).

## Storage Management

### Capacity Planning

**Storage Requirements:**
- Daily incremental: ~1-5 MB per day
- Weekly full: ~50-500 MB per backup
- Monthly retention: 2-5 GB
- Yearly retention: 10-20 GB

**Current Status:**
- Check disk space: `df -h backups/gmail`
- Check backup folder size: `du -sh backups/gmail`
- Count backup files: `find backups/gmail -name "*.mbox" | wc -l`

### Retention Policy

**Recommended Policy:**
- Keep incremental backups for 30 days
- Keep last 10-20 full backups
- Archive important backups to external storage

**Automated Cleanup:**
```bash
# Preview what would be deleted
python scripts/cleanup_backups.py --keep-days 30 --keep-count 10 --dry-run

# Apply retention policy
python scripts/cleanup_backups.py --keep-days 30 --keep-count 10
```

**Add to Cron:**
```cron
# Daily cleanup at 3 AM (after backup at 2 AM)
0 3 * * * /path/to/mcp-google-services/scripts/cleanup_backups.py --keep-days 30 --keep-count 10
```

For detailed storage management, see [Storage Management Guide](STORAGE_MANAGEMENT.md).

## Restore Procedures

### Before Restoring

**Validate MBOX File:**
```bash
# Check file format
file backups/gmail/gmail_backup_*.mbox

# Count messages
grep -c "^From " backups/gmail/gmail_backup_*.mbox

# Verify file size
ls -lh backups/gmail/gmail_backup_*.mbox
```

### Restore to Email Client

**Mozilla Thunderbird (Recommended):**
1. Install ImportExportTools NG add-on
2. Tools > ImportExportTools NG > Import mbox file
3. Select MBOX file and destination folder
4. Click Import

**Apple Mail (macOS):**
1. File > Import Mailboxes...
2. Select "Files in mbox format"
3. Choose MBOX file
4. Select destination mailbox

**Other Clients:**
- See [Restore Guide](RESTORE_GUIDE.md) for detailed procedures

### Verify Restore

After importing:
1. Check message count matches backup
2. Open several messages to verify content
3. Test search functionality
4. Verify attachments (if any)

For detailed restore procedures, see [Restore Guide](RESTORE_GUIDE.md).

## Maintenance

### Regular Tasks

**Daily:**
- Monitor backup logs for errors
- Verify backups are created successfully

**Weekly:**
- Review backup file sizes and count
- Check disk space availability
- Test restore from recent backup

**Monthly:**
- Review retention policy effectiveness
- Archive important backups to external storage
- Update documentation if procedures change

### Monitoring

**Check Backup Status:**
```bash
# View recent backups
ls -lht backups/gmail/*.mbox | head -5

# Check backup state
cat backups/gmail/backup_state.json

# View backup logs
tail -20 logs/backup.log
```

**Storage Monitoring:**
```bash
# Check disk space
df -h backups/gmail

# Check backup folder size
du -sh backups/gmail

# Count backup files
find backups/gmail -name "*.mbox" | wc -l
```

### Backup Verification

**Validate Backup Integrity:**
```bash
# Check MBOX file format
file backups/gmail/gmail_backup_*.mbox

# Count messages
grep -c "^From " backups/gmail/gmail_backup_*.mbox

# Test restore (import into email client)
```

**Periodic Restore Testing:**
- Monthly: Import recent backup into test email client
- Verify all messages are accessible
- Test search and filtering
- Verify attachments are intact

## Troubleshooting

### Common Issues

**Backup Fails:**
- Check authentication: Verify `config/credentials.json` exists
- Check Gmail API is enabled in Google Cloud Console
- Review error messages in logs: `tail -f logs/backup.log`
- Test authentication: `python scripts/backup_gmail.py --type incremental --max-results 1`

**Cron Job Not Running:**
- Verify cron service is running
- Check cron syntax: `crontab -l`
- Use absolute paths in cron
- Check cron logs for errors
- Test script manually first

**Storage Issues:**
- Run cleanup script: `python scripts/cleanup_backups.py --keep-days 7`
- Check disk space: `df -h`
- Move old backups to external storage
- Adjust retention policy

**Restore Issues:**
- Validate MBOX file format
- Try different email client (Thunderbird recommended)
- Check file permissions
- Verify MBOX file is not corrupted

For detailed troubleshooting, see [Troubleshooting Guide](TROUBLESHOOTING.md).

## Complete Workflow Example

### Initial Setup (One-Time)

```bash
# 1. Install dependencies
cd mcp-google-services
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. Configure credentials
# Place OAuth credentials in config/credentials.json

# 3. Test backup
python scripts/backup_gmail.py --type incremental --max-results 10

# 4. Set up automated scheduling
cp scripts/run_backup.sh.example scripts/run_backup.sh
# Edit paths in run_backup.sh
chmod +x scripts/run_backup.sh

# 5. Add to crontab
crontab -e
# Add: 0 2 * * * /path/to/mcp-google-services/scripts/run_backup.sh
```

### Daily Operations

**Automated (via Cron):**
- Daily incremental backup at 2 AM
- Cleanup old backups at 3 AM
- Logs written to `logs/backup.log`

**Manual (if needed):**
```bash
# Manual backup
python scripts/backup_gmail.py --type incremental

# Check backup status
ls -lht backups/gmail/*.mbox | head -5

# View logs
tail -f logs/backup.log
```

### Weekly Operations

**Automated:**
- Weekly full backup on Sunday at 3 AM

**Manual:**
```bash
# Full backup
python scripts/backup_gmail.py --type full

# Cleanup old backups
python scripts/cleanup_backups.py --keep-days 30 --keep-count 10

# Verify restore (test import)
# Import recent backup into email client
```

### Monthly Operations

```bash
# Review storage usage
du -sh backups/gmail
df -h backups/gmail

# Archive important backups
# Copy to external storage or cloud

# Test restore
# Import backup into email client and verify
```

## Best Practices

### Backup Strategy

1. **Use Incremental for Regular Backups**
   - Faster and more efficient
   - Lower API quota usage
   - Smaller backup files

2. **Use Full Backups Periodically**
   - Weekly or monthly full backups
   - Complete mailbox snapshot
   - Independent of incremental chain

3. **Test Restores Regularly**
   - Monthly restore test
   - Verify backup integrity
   - Ensure recovery procedures work

### Storage Management

1. **Implement Retention Policy**
   - Keep 30 days of incremental backups
   - Keep last 10-20 full backups
   - Archive important backups externally

2. **Monitor Storage Usage**
   - Weekly storage checks
   - Set up alerts for low disk space
   - Plan for storage expansion

3. **Automate Cleanup**
   - Run cleanup after backups
   - Use cron for automated cleanup
   - Review cleanup logs regularly

### Security

1. **Protect Credentials**
   - Store `config/credentials.json` securely
   - Use file permissions: `chmod 600 config/credentials.json`
   - Don't commit credentials to version control

2. **Secure Backup Files**
   - Consider encryption for sensitive backups
   - Store backups in secure location
   - Limit access to backup files

3. **Regular Updates**
   - Keep dependencies updated
   - Review security advisories
   - Update OAuth credentials if compromised

## Related Documentation

- [**Scheduling Guide**](SCHEDULING_GUIDE.md) - Detailed scheduling setup
- [**Storage Management**](STORAGE_MANAGEMENT.md) - Storage and retention policies
- [**Restore Guide**](RESTORE_GUIDE.md) - Detailed restore procedures
- [**Backup System**](services/BACKUP_SYSTEM.md) - How backups work
- [**Troubleshooting Guide**](TROUBLESHOOTING.md) - Common issues and solutions
- [**Authentication Guide**](AUTHENTICATION.md) - Authentication setup

## Quick Reference

### Common Commands

```bash
# Manual backup
python scripts/backup_gmail.py --type incremental

# Full backup
python scripts/backup_gmail.py --type full

# Cleanup old backups (preview)
python scripts/cleanup_backups.py --keep-days 30 --dry-run

# Cleanup old backups (execute)
python scripts/cleanup_backups.py --keep-days 30 --keep-count 10

# Check backup status
ls -lht backups/gmail/*.mbox | head -5
cat backups/gmail/backup_state.json

# View logs
tail -f logs/backup.log

# Validate MBOX file
grep -c "^From " backups/gmail/gmail_backup_*.mbox
```

### Configuration Files

- `config/credentials.json` - OAuth credentials (required)
- `config/config.json` - Server configuration (optional)
- `backups/gmail/backup_state.json` - Backup state tracking
- `logs/backup.log` - Backup execution logs

### Important Paths

- Backup folder: `backups/gmail/`
- Logs folder: `logs/`
- Config folder: `config/`
- Scripts folder: `scripts/`

---

**Last Updated**: November 2025  
**MCP Server Version**: 1.0.0

**For Support:**
- Documentation: See related guides above
- Issues: [GitHub Issues](https://github.com/CloudBoostUP/mcp-google-services/issues)
- Email: support@cloudboostup.com

