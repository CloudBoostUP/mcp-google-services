# Backup System

This document describes the Gmail backup system implemented in the Google Services MCP Server.

## Overview

The backup system provides two types of backups:
- **Incremental Backup**: Only backs up new or changed messages since last backup
- **Full Backup**: Backs up all messages matching the query criteria

## Backup Types

### Incremental Backup

Incremental backups only retrieve messages that have been created or modified since the last backup. This is more efficient for regular, scheduled backups.

#### How It Works

1. **Load Last Backup State**: Reads `backup_state.json` to get timestamp of last backup
2. **Build Query**: Constructs Gmail query with `after:YYYY/MM/DD` filter
3. **Fetch Messages**: Retrieves only messages after the last backup date
4. **Generate MBOX**: Creates MBOX file with new messages
5. **Update State**: Updates `backup_state.json` with new backup timestamp

#### Example

```python
from mcp_google_services.services.gmail.backup import GmailBackup

backup_service = GmailBackup(api=gmail_api, config=config)

# Perform incremental backup
result = backup_service.incremental_backup(
    user_id="me",
    max_results=1000
)

# Result includes:
# - success: bool
# - message_count: int
# - backup_path: str
# - messages_processed: int
# - messages_failed: int
```

#### Advantages

- **Efficiency**: Only processes new messages
- **Speed**: Faster execution for large mailboxes
- **Quota Savings**: Uses fewer API quota units
- **Storage**: Smaller backup files

#### Limitations

- **Dependency on State**: Requires previous backup state file
- **Date Precision**: Uses date (not timestamp) for query filtering
- **Deleted Messages**: Cannot detect deleted messages (messages removed from Gmail)

### Full Backup

Full backups retrieve all messages matching the query criteria, regardless of previous backups.

#### How It Works

1. **Build Query**: Uses provided query or no query (all messages)
2. **Fetch Messages**: Retrieves all messages matching criteria
3. **Generate MBOX**: Creates MBOX file with all messages
4. **No State Update**: Does not update backup state (incremental backups track state)

#### Example

```python
# Perform full backup
result = backup_service.full_backup(
    user_id="me",
    query="from:important@example.com",
    max_results=10000
)
```

#### Advantages

- **Complete**: Captures all messages matching criteria
- **Independent**: No dependency on previous backups
- **Verification**: Can be used to verify backup integrity

#### Limitations

- **Time**: Slower for large mailboxes
- **Quota**: Uses more API quota units
- **Storage**: Larger backup files

## Backup Process Flow

### 1. Initialization

```python
# Initialize services
config = Config()
auth_manager = AuthManager(config)
credentials = auth_manager.get_credentials(user_id)
gmail_api = GmailAPI(credentials=credentials)
backup_service = GmailBackup(api=gmail_api, config=config)
```

### 2. Message Collection

**Incremental Backup:**
```python
# Get last backup time
last_backup_time = backup_service._get_last_backup_time(user_id)

# Build query with date filter
if last_backup_time:
    query = f"after:{last_backup_time.strftime('%Y/%m/%d')}"
else:
    query = None  # First backup - get all messages

# List messages
message_ids = gmail_api.list_messages(
    user_id=user_id,
    query=query,
    max_results=max_results
)
```

**Full Backup:**
```python
# Use provided query or get all messages
message_ids = gmail_api.list_messages(
    user_id=user_id,
    query=query,  # Can be None for all messages
    max_results=max_results
)
```

### 3. Batch Processing

Messages are processed in batches for efficiency:

```python
batch_size = 100
with MBOXGenerator(backup_path) as mbox:
    for i in range(0, len(message_ids), batch_size):
        batch = message_ids[i:i + batch_size]
        
        # Get messages in raw format
        messages = gmail_api.batch_get_messages(
            user_id=user_id,
            message_ids=batch,
            format="raw"  # Raw format for MBOX generation
        )
        
        # Add to MBOX
        for message in messages:
            mbox.add_message(message)
```

### 4. State Management

**Incremental Backup State Update:**
```python
if result.success:
    backup_service._update_backup_state(user_id, datetime.now())
```

**State File Structure:**
```json
{
  "user@example.com": {
    "last_backup_time": "2024-11-04T11:25:45",
    "last_backup_type": "incremental"
  }
}
```

## Backup Configuration

### Configuration Options

```json
{
  "services": {
    "gmail": {
      "backup_folder": "backups/gmail",
      "max_messages_per_batch": 100,
      "max_messages_per_backup": 1000
    }
  }
}
```

### Environment Variables

```bash
export MCP_GMAIL__BACKUP_FOLDER="backups/gmail"
export MCP_GMAIL__MAX_MESSAGES_PER_BACKUP=1000
```

## Backup Results

### BackupResult Structure

```python
@dataclass
class BackupResult:
    success: bool
    message_count: int
    backup_path: str
    start_time: datetime
    end_time: Optional[datetime] = None
    error: Optional[str] = None
    messages_processed: int = 0
    messages_failed: int = 0
```

### Example Result

```python
BackupResult(
    success=True,
    message_count=100,
    backup_path="backups/gmail/gmail_backup_incremental_20241104_112545.mbox",
    start_time=datetime(2024, 11, 4, 11, 25, 45),
    end_time=datetime(2024, 11, 4, 11, 26, 30),
    messages_processed=100,
    messages_failed=0
)
```

## Error Handling

### Message Processing Errors

If individual messages fail to process:

1. **Log Warning**: Log message ID and error
2. **Continue Processing**: Skip failed message, continue with next
3. **Track Failures**: Increment `messages_failed` counter
4. **Report**: Include failed count in result

### Backup Failures

If entire backup fails:

1. **Error Message**: Return error message in result
2. **Partial Results**: If some messages processed, include in result
3. **State Not Updated**: Don't update backup state on failure
4. **Logging**: Log detailed error information

## Best Practices

### Backup Strategy

1. **Regular Incremental Backups**: Daily or weekly incremental backups
2. **Periodic Full Backups**: Monthly or quarterly full backups
3. **Verification**: Verify backup files after creation
4. **Multiple Locations**: Store backups in multiple locations

### Performance Optimization

1. **Query Filtering**: Use queries to filter messages (e.g., by date, sender)
2. **Batch Size**: Use appropriate batch size (100 messages)
3. **Raw Format**: Always use raw format for MBOX generation
4. **Parallel Processing**: Use async operations for concurrent retrieval

### Storage Management

1. **Cleanup**: Remove old backup files periodically
2. **Compression**: Compress old backups to save space
3. **Verification**: Verify backup integrity regularly
4. **Metadata**: Track backup metadata in state file

## Troubleshooting

### Common Issues

#### No Messages Backed Up

**Possible Causes:**
- No new messages since last backup (incremental)
- Query filter too restrictive
- API quota exceeded

**Solutions:**
- Check last backup timestamp
- Verify query syntax
- Check API quota usage

#### Backup State File Missing

**Solution:**
- First backup will create state file
- Incremental backup will behave as full backup if state missing

#### Messages Not Appearing in Backup

**Possible Causes:**
- Date filter too restrictive
- Query filter excludes messages
- Messages deleted from Gmail

**Solutions:**
- Check query syntax
- Verify date filter
- Perform full backup to verify

### Verification

#### Check Backup State

```python
from mcp_google_services.services.gmail.backup import GmailBackup

backup_service = GmailBackup(api=gmail_api, config=config)
last_backup = backup_service._get_last_backup_time("me")
print(f"Last backup: {last_backup}")
```

#### Verify MBOX File

```bash
# Count messages
grep -c "^From " backups/gmail/gmail_backup_*.mbox

# Check file size
ls -lh backups/gmail/gmail_backup_*.mbox

# View first message
head -50 backups/gmail/gmail_backup_*.mbox
```

## MCP Tool Usage

### Using MCP Tools

The backup system is accessible via MCP tools in Cursor:

```
"Backup my Gmail messages"
"Create a full backup of my Gmail"
"Do an incremental backup of my emails"
"Backup messages from the last month"
```

### Tool Parameters

- `user_id`: Gmail user ID (default: "me")
- `backup_type`: "incremental" or "full" (default: "incremental")
- `max_results`: Maximum number of messages (default: 1000)
- `query`: Optional Gmail search query

## Future Enhancements

### Planned Features

- **Scheduling**: Automated backup scheduling (cron-based)
- **Compression**: Optional backup compression
- **Encryption**: Optional backup encryption
- **Progress Tracking**: Real-time backup progress
- **Resume Support**: Resume interrupted backups
- **Deduplication**: Detect and skip duplicate messages

