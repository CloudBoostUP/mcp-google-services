# MBOX Generation Process

This document describes how the Google Services MCP Server generates MBOX files from Gmail messages.

## Overview

MBOX is a standard email format (RFC 4155) that allows emails to be stored in a single text file. The MCP server generates RFC 4155 compliant MBOX files from Gmail messages for portability and backup purposes.

## MBOX Format Specification

### RFC 4155 Compliance

The MBOX format requires:
1. **"From " Separator Line**: Each message starts with a line beginning with "From " (space included)
2. **Message Content**: Full RFC 822 compliant email message
3. **Message Separator**: Empty line between messages

### Format Structure

```
From sender@example.com  Mon, 01 Jan 2024 12:00:00 +0000
Message-ID: <message-id>
From: sender@example.com
To: recipient@example.com
Subject: Email Subject
Date: Mon, 01 Jan 2024 12:00:00 +0000
Content-Type: text/plain; charset=utf-8

Email body content here

From sender2@example.com  Mon, 01 Jan 2024 13:00:00 +0000
Message-ID: <message-id-2>
...
```

## Implementation

### MBOXGenerator Class

The `MBOXGenerator` class (`src/mcp_google_services/services/gmail/mbox.py`) handles MBOX file creation.

#### Key Features

- **RFC 4155 Compliant**: Generates standard MBOX format
- **Raw Message Support**: Handles Gmail API raw format directly
- **Encoding Support**: UTF-8 encoding with proper header handling
- **Context Manager**: Can be used with `with` statement
- **Message Counting**: Tracks number of messages written

#### Methods

##### `open()`

Opens MBOX file for writing in append binary mode.

```python
mbox = MBOXGenerator("backups/gmail_backup.mbox")
mbox.open()
```

##### `add_message(message)`

Adds a message to the MBOX file. Accepts:
- Raw Gmail API message (with `raw` field) - **Preferred for performance**
- Parsed message dictionary (from EmailParser)

```python
# Raw message (preferred)
message = gmail_api.get_message(message_id, format="raw")
mbox.add_message(message)

# Parsed message
parsed = EmailParser.parse_message(message)
mbox.add_message(parsed)
```

##### `close()`

Closes the MBOX file.

```python
mbox.close()
```

##### Context Manager Usage

```python
with MBOXGenerator("backups/gmail_backup.mbox") as mbox:
    for message in messages:
        mbox.add_message(message)
# File automatically closed
```

### Raw Message Processing

The MBOX generator prioritizes raw message format for performance:

1. **Decode Base64**: Decodes Gmail API's base64url-encoded raw message
2. **Extract From Header**: Parses email to extract "From" header for separator line
3. **Generate Separator**: Creates RFC 4155 "From " separator line
4. **Write Message**: Writes raw message bytes directly to file

**Advantages:**
- No parsing overhead
- Preserves original message format exactly
- Faster processing for large backups
- Handles complex multipart messages correctly

### Parsed Message Processing

If raw format is not available, the generator uses parsed messages:

1. **Format From Line**: Generates "From " separator from parsed message headers
2. **Convert to RFC 822**: Uses `EmailParser.to_rfc822()` to convert parsed message
3. **Write Message**: Writes formatted message bytes

**Fallback Path:**
- Used when raw format is not available
- Handles parsed message dictionaries
- Slower but more flexible

## Email Parsing

### EmailParser Class

The `EmailParser` class (`src/mcp_google_services/services/gmail/parser.py`) parses Gmail API message objects into structured format.

#### Parse Process

1. **Header Parsing**: Extracts and decodes email headers
2. **Body Extraction**: Separates text and HTML body parts
3. **Attachment Handling**: Identifies and extracts attachments
4. **Multipart Handling**: Recursively processes multipart messages

#### Key Methods

##### `parse_message(message)`

Parses a Gmail API message object into a structured dictionary.

**Returns:**
```python
{
    "id": "message-id",
    "threadId": "thread-id",
    "snippet": "Message snippet...",
    "headers": {
        "from": "sender@example.com",
        "to": "recipient@example.com",
        "subject": "Subject",
        "date": "Mon, 01 Jan 2024 12:00:00 +0000"
    },
    "body": {
        "text": "Plain text body",
        "html": "<html>HTML body</html>"
    },
    "attachments": [...],
    "date": datetime object
}
```

##### `to_rfc822(message)`

Converts parsed message dictionary back to RFC 822 format bytes.

**Handles:**
- Multipart messages (text + HTML)
- Headers encoding
- Body encoding
- Content-Type headers

## Backup Process

### Message Retrieval Strategy

For optimal performance, the backup process uses raw format:

```python
# 1. List messages (metadata only)
message_ids = gmail_api.list_messages(user_id, query, max_results)

# 2. Batch get messages in raw format
messages = gmail_api.batch_get_messages(
    user_id=user_id,
    message_ids=message_ids,
    format="raw"  # Use raw format for MBOX
)

# 3. Add directly to MBOX (no parsing needed)
with MBOXGenerator(backup_path) as mbox:
    for message in messages:
        mbox.add_message(message)
```

### Performance Considerations

1. **Raw Format**: Use raw format when possible (faster, no parsing)
2. **Batch Processing**: Process messages in batches (100 at a time)
3. **Streaming**: Write messages as they're retrieved (not all at once)
4. **Error Handling**: Continue processing even if individual messages fail

## File Structure

### Backup Files

Backups are stored in `backups/gmail/` directory:

```
backups/gmail/
├── gmail_backup_incremental_20241104_112545.mbox
├── gmail_backup_full_20241104_120000.mbox
└── backup_state.json
```

### File Naming Convention

- **Incremental**: `gmail_backup_incremental_YYYYMMDD_HHMMSS.mbox`
- **Full**: `gmail_backup_full_YYYYMMDD_HHMMSS.mbox`

### Backup State File

`backup_state.json` tracks backup metadata:

```json
{
  "user@example.com": {
    "last_backup_time": "2024-11-04T11:25:45",
    "last_backup_type": "incremental",
    "message_count": 1000
  }
}
```

## Encoding and Character Handling

### UTF-8 Encoding

- All MBOX files use UTF-8 encoding
- Headers are properly decoded from Gmail API format
- Non-ASCII characters are preserved correctly

### Header Decoding

The parser handles:
- RFC 2047 encoded headers (e.g., `=?UTF-8?B?...?=`)
- Multiple header encodings
- Character set detection

### Body Encoding

- Plain text: UTF-8
- HTML: UTF-8 with proper Content-Type headers
- Attachments: Base64 encoded (preserved from Gmail API)

## Error Handling

### Message Processing Errors

If a message fails to process:
1. Log warning with message ID
2. Continue with next message
3. Track failed messages in backup result

### File Writing Errors

- File permissions: Ensure backup directory is writable
- Disk space: Check available space before starting backup
- Interrupted writes: File may be corrupted, delete and retry

## Validation

### MBOX File Validation

To validate generated MBOX files:

```bash
# Check file format
file backups/gmail/gmail_backup_*.mbox

# Count messages (Unix/Mac)
grep -c "^From " backups/gmail/gmail_backup_*.mbox

# View first message
head -50 backups/gmail/gmail_backup_*.mbox
```

### Email Client Import

MBOX files can be imported into:
- **Thunderbird**: File > Import > Import from File > MBOX
- **Apple Mail**: File > Import Mailboxes > Files in mbox format
- **Outlook**: Use third-party tools or converters
- **Gmail**: Upload via Google Takeout or use IMAP

## Best Practices

### Backup Strategy

1. **Incremental Backups**: Use incremental backups for regular operations
2. **Full Backups**: Perform full backups periodically (weekly/monthly)
3. **Verification**: Verify backup files after creation
4. **Storage**: Store backups in multiple locations

### Performance Tips

1. **Use Raw Format**: Always use raw format for MBOX generation
2. **Batch Size**: Process 100 messages per batch
3. **Parallel Processing**: Use async operations for concurrent retrieval
4. **Stream Writing**: Write messages as they're retrieved

### File Management

1. **Cleanup**: Remove old backup files periodically
2. **Compression**: Compress old backups to save space
3. **Verification**: Verify backup integrity regularly
4. **Backup Metadata**: Track backup metadata in state file

## References

- [RFC 4155 - The application/mbox Format](https://tools.ietf.org/html/rfc4155)
- [RFC 822 - Standard for ARPA Internet Text Messages](https://tools.ietf.org/html/rfc822)
- [RFC 2047 - MIME Part Three: Message Header Extensions](https://tools.ietf.org/html/rfc2047)

