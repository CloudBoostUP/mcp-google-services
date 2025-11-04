# Gmail API Integration

This document describes how the Google Services MCP Server integrates with the Gmail API to provide email backup and management capabilities.

## Overview

The Gmail API integration provides:
- Message listing and retrieval
- Label management
- Message filtering and search
- Batch operations
- Rate limit management

## Authentication

### Required Scopes

The Gmail API integration requires the following OAuth 2.0 scopes:

- `https://www.googleapis.com/auth/gmail.readonly` - Read-only access to Gmail messages and metadata

**Note**: The `gmail.metadata` scope does not support query parameters, so we use `gmail.readonly` for full functionality.

### Authentication Methods

1. **Application Default Credentials (ADC)**: 
   - Uses OAuth 2.0 credentials file (required for Gmail API)
   - Automatically manages token refresh
   - Stores credentials securely in system keyring

2. **OAuth 2.0 Credentials File**:
   - Requires `config/credentials.json` file
   - Prompts for OAuth consent on first use
   - Stores tokens securely using keyring

See [Authentication Guide](../AUTHENTICATION.md) for detailed setup instructions.

## Gmail API Client

The `GmailAPI` class (`src/mcp_google_services/services/gmail/api.py`) provides a high-level interface to the Gmail API.

### Key Features

- **Rate Limiting**: Automatically manages API quota (250 requests/second default)
- **Error Handling**: Robust retry logic with exponential backoff
- **Token Refresh**: Automatic credential refresh when expired
- **Batch Operations**: Efficient batch message retrieval

### API Methods

#### `list_messages(user_id, query=None, max_results=None)`

Lists messages in the user's Gmail mailbox with optional filtering.

**Parameters:**
- `user_id` (str): User email address or "me" (default: "me")
- `query` (str, optional): Gmail search query (e.g., "from:example@gmail.com", "has:attachment")
- `max_results` (int, optional): Maximum number of messages to return

**Returns:** List of message metadata dictionaries

**Example:**
```python
api = GmailAPI(credentials=credentials)
messages = api.list_messages(
    user_id="me",
    query="from:example@gmail.com newer_than:7d",
    max_results=100
)
```

**Quota Cost:** 5 units per call

#### `get_message(user_id, message_id, format="full")`

Retrieves a specific message by ID.

**Parameters:**
- `user_id` (str): User email address or "me"
- `message_id` (str): Gmail message ID
- `format` (str): Message format - "full", "metadata", "minimal", "raw" (default: "full")

**Returns:** Message object dictionary

**Quota Cost:** 5 units per call

#### `batch_get_messages(user_id, message_ids, format="full")`

Retrieves multiple messages efficiently.

**Parameters:**
- `user_id` (str): User email address or "me"
- `message_ids` (list): List of message IDs to retrieve
- `format` (str): Message format (default: "full")

**Returns:** List of message objects

**Note:** Gmail API doesn't have a native `batchGet` endpoint, so this method fetches messages individually with rate limiting.

**Quota Cost:** 5 units per message

#### `list_labels(user_id)`

Lists all labels in the user's Gmail mailbox.

**Parameters:**
- `user_id` (str): User email address or "me"

**Returns:** List of label dictionaries

**Quota Cost:** 1 unit per call

## Gmail Search Queries

The Gmail API supports powerful search queries for filtering messages:

### Basic Queries

- `from:example@gmail.com` - Messages from specific sender
- `to:example@gmail.com` - Messages to specific recipient
- `subject:search term` - Search in subject line
- `has:attachment` - Messages with attachments
- `is:unread` - Unread messages
- `is:read` - Read messages
- `label:INBOX` - Messages in specific label

### Date Queries

- `newer_than:7d` - Messages newer than 7 days
- `older_than:30d` - Messages older than 30 days
- `after:2024/01/01` - Messages after date (format: YYYY/MM/DD)
- `before:2024/12/31` - Messages before date

### Combined Queries

- `from:example@gmail.com newer_than:7d` - From sender in last 7 days
- `has:attachment is:unread` - Unread messages with attachments

**Note:** The `gmail.metadata` scope doesn't support query parameters. Use `gmail.readonly` scope for full search functionality.

## Rate Limiting

### Gmail API Quotas

- **Quota per second:** 250 requests/second (default)
- **Burst allowance:** 500 requests (default)
- **Daily quota:** 1,000,000,000 quota units per day

### Rate Limiter Implementation

The `RateLimiter` class (`src/mcp_google_services/core/rate_limiter.py`) uses a token bucket algorithm:

- **Token Bucket:** Starts with full burst capacity
- **Automatic Refill:** Tokens refill at quota rate per second
- **Request Tracking:** Tracks requests per second to prevent bursts
- **Thread-Safe:** Safe for concurrent operations

### Quota Costs

Different operations have different quota costs:

- `messages.list()`: 5 units
- `messages.get()`: 5 units
- `labels.list()`: 1 unit
- `labels.get()`: 1 unit

## Error Handling

### Common Errors

1. **429 Too Many Requests**
   - **Cause:** Rate limit exceeded
   - **Handling:** Automatic retry with exponential backoff
   - **Wait Time:** Calculated based on quota and current usage

2. **401 Unauthorized**
   - **Cause:** Expired or invalid credentials
   - **Handling:** Automatic token refresh, then retry
   - **Fallback:** Re-authenticate if refresh fails

3. **403 Forbidden**
   - **Cause:** Insufficient permissions or API not enabled
   - **Handling:** Return error with helpful message
   - **Solution:** Check API is enabled and scopes are correct

4. **404 Not Found**
   - **Cause:** Message or label doesn't exist
   - **Handling:** Skip and continue (for batch operations)
   - **Logging:** Warning logged for debugging

### Retry Logic

All API calls implement retry logic:

- **Max Retries:** 3 attempts
- **Backoff Factor:** 1.5 (exponential backoff)
- **Retryable Errors:** 429 (rate limit), 401 (unauthorized), 500-503 (server errors)

## Best Practices

### Efficient Message Retrieval

1. **Use Search Queries:** Filter messages server-side rather than retrieving all messages
2. **Batch Operations:** Use `batch_get_messages` for multiple messages
3. **Pagination:** Use `pageToken` for large result sets
4. **Format Selection:** Use "raw" format for MBOX generation, "full" for parsing

### Rate Limit Management

1. **Respect Quotas:** Always use the rate limiter
2. **Monitor Usage:** Track quota usage to avoid exhaustion
3. **Batch Wisely:** Group operations to minimize API calls
4. **Error Handling:** Implement retry logic for transient failures

### Performance Optimization

1. **Parallel Processing:** Use async/await for concurrent operations
2. **Caching:** Cache label lists and metadata
3. **Incremental Updates:** Use incremental backups when possible
4. **Selective Fetching:** Only fetch needed message parts

## Example Usage

```python
from mcp_google_services.services.gmail.api import GmailAPI
from mcp_google_services.core.auth import AuthManager
from mcp_google_services.utils.config import Config

# Initialize
config = Config()
auth_manager = AuthManager(config)
credentials = auth_manager.get_credentials("me")

# Create API client
gmail_api = GmailAPI(credentials=credentials)

# List recent messages
messages = gmail_api.list_messages(
    user_id="me",
    query="newer_than:7d",
    max_results=100
)

# Get specific message
message = gmail_api.get_message(
    user_id="me",
    message_id=messages[0]["id"],
    format="raw"
)

# List labels
labels = gmail_api.list_labels(user_id="me")
```

## References

- [Gmail API Documentation](https://developers.google.com/gmail/api)
- [Gmail API Quotas](https://developers.google.com/gmail/api/reference/quota)
- [Gmail Search Operators](https://support.google.com/mail/answer/7190)

