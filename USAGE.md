# Google Services MCP Server - Usage Guide

## Testing the MCP Server in Cursor

Now that the MCP server is configured in Cursor, you can test it using natural language commands.

### Available Tools

1. **gmail_list_labels** - List Gmail Labels**
   ```
   "List my Gmail labels"
   "Show me all Gmail labels"
   ```

2. **gmail_list_messages - List Gmail Messages**
   ```
   "List my Gmail messages"
   "Show me recent emails from last week"
   "List messages with attachments"
   "Find emails from sender@example.com"
   ```

3. **gmail_backup - Backup Gmail Messages**
   ```
   "Backup my Gmail messages"
   "Create a full backup of my Gmail"
   "Do an incremental backup of my emails"
   "Backup messages from the last month"
   ```

4. **gmail_export - Export Gmail Messages**
   ```
   "Export my Gmail to JSON"
   "Export my emails to CSV format"
   "Export recent messages to MBOX"
   "Export emails with attachments to JSON"
   ```

## Prerequisites for Testing

Before using the tools, you need:

1. **OAuth Credentials**: Place your Google OAuth 2.0 credentials in:
   ```
   config/credentials.json
   ```

2. **Gmail API Enabled**: Ensure Gmail API is enabled in your Google Cloud Project

3. **First-Time Authentication**: On first use, the server will open a browser for OAuth consent

## Example Usage Scenarios

### Scenario 1: Quick Email Check
```
You: "List my Gmail labels"
Cursor: Uses gmail_list_labels tool → Shows all your Gmail labels
```

### Scenario 2: Backup Recent Emails
```
You: "Backup my recent Gmail messages from last week"
Cursor: Uses gmail_backup tool with query="newer_than:7d" → Creates MBOX backup
```

### Scenario 3: Export for Analysis
```
You: "Export my Gmail to CSV so I can analyze it"
Cursor: Uses gmail_export tool with format="csv" → Creates CSV file with email metadata
```

### Scenario 4: Find Specific Emails
```
You: "List messages from my boss in the last month"
Cursor: Uses gmail_list_messages with query="from:boss@company.com newer_than:30d"
```

## Troubleshooting

### "No server info found" Error
- **Solution**: Restart Cursor completely (quit and reopen)

### "Authentication failed" Error
- **Solution**: Ensure `config/credentials.json` exists with valid OAuth credentials

### "Credentials not found" Error
- **Solution**: Download OAuth 2.0 credentials from Google Cloud Console and place in `config/credentials.json`

### Server Loads Multiple Times
- **Solution**: This is normal during development. Cursor may retry initialization. The server should stabilize after a few seconds.

## Verification

To verify the server is working:

1. **Check Cursor MCP Status**: Look for "google-services" in Cursor's MCP server list
2. **Test a Simple Command**: Try "List my Gmail labels" - should work if credentials are set up
3. **Check Logs**: Any errors will appear in Cursor's MCP logs

## Next Steps

Once the server is confirmed working:
- Set up OAuth credentials for your Gmail account
- Test with a small backup first (max_results=10)
- Verify backup files are created correctly
- Test export in different formats

