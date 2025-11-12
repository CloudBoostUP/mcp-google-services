# Troubleshooting Guide

This guide helps you resolve common issues with the Google Services MCP Server.

## Authentication Issues

### Error: "No authentication credentials found"

**Symptoms:**
- Tool execution fails with authentication error
- Error message indicates no credentials available

**Causes:**
- OAuth credentials file not found
- Credentials file in wrong location
- Gmail API requires OAuth credentials (not ADC)

**Solutions:**

1. **Set Up OAuth Credentials File (Required for Gmail API):**
   - Download OAuth 2.0 credentials from [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
   - Create OAuth client ID (Desktop app type)
   - Place in `config/credentials.json`
   - Ensure file has correct permissions
   
   ```bash
   # Check if file exists
   ls -la config/credentials.json
   
   # Check file permissions
   chmod 600 config/credentials.json
   ```

2. **Verify Credentials File Location:**
   ```bash
   # Verify file exists
   ls -la config/credentials.json
   
   # Verify file format (should be JSON)
   head -5 config/credentials.json
   ```

**Important:** `gcloud auth application-default login` does NOT work for Gmail API because it doesn't support Gmail scopes. You must use OAuth credentials file.

### Error: "Gmail API scopes are required but not present"

**Symptoms:**
- Authentication succeeds but Gmail API calls fail
- Error mentions missing Gmail scopes

**Causes:**
- Attempting to use Application Default Credentials (ADC) which don't support Gmail scopes
- `gcloud auth application-default login` does NOT support Gmail scopes
- OAuth credentials file not properly configured

**Solutions:**

1. **Use OAuth Credentials File (Required):**
   - Gmail API **requires** OAuth 2.0 credentials file
   - Download OAuth 2.0 credentials from [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
   - Create OAuth client ID (Desktop app type)
   - Place in `config/credentials.json`
   - First use will prompt for OAuth consent with Gmail scopes

2. **Verify OAuth Consent Screen:**
   - Ensure Gmail API is enabled in Google Cloud Project
   - Configure OAuth consent screen with Gmail scopes
   - Add scopes: `https://www.googleapis.com/auth/gmail.readonly`
   - Verify test users are added (if app is in testing mode)

3. **Re-authenticate:**
   - Delete stored tokens: `rm config/tokens.json` (if exists)
   - Run MCP server again to trigger OAuth flow

### Error: "Permission denied" or "403 Forbidden"

**Symptoms:**
- API calls return 403 errors
- Access denied messages

**Causes:**
- Gmail API not enabled in Google Cloud Project
- OAuth consent screen not configured
- App not verified (for production apps)

**Solutions:**

1. **Enable Gmail API:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Navigate to "APIs & Services" > "Library"
   - Search for "Gmail API"
   - Click "Enable"

2. **Configure OAuth Consent Screen:**
   - Go to "APIs & Services" > "OAuth consent screen"
   - Fill in required information
   - Add scopes: `https://www.googleapis.com/auth/gmail.readonly`, `https://www.googleapis.com/auth/gmail.send`
   - Add test users (if app is in testing mode)

3. **Verify App Status:**
   - For testing: App must be in "Testing" mode with test users added
   - For production: App must be verified by Google

### Error: "access_denied" - OAuth Consent Screen

**Symptoms:**
- Error 403: access_denied
- Message: "Gmail MCP Server has not completed the Google verification process"
- OAuth flow fails during consent

**Causes:**
- OAuth consent screen is in "Testing" mode
- Your email address not added as a test user
- App not verified (for production apps)

**Solutions:**

1. **Add Yourself as Test User (Quick Fix - 2 minutes):**
   - Go to [Google Cloud Console OAuth Consent Screen](https://console.cloud.google.com/apis/credentials/consent)
   - Scroll down to **"Test users"** section
   - Click **"+ ADD USERS"**
   - Enter your Gmail address (the one you want to use)
   - Click **"ADD"**
   - Try authentication again - it should work now! ✅

2. **Verify Test Users:**
   - Ensure your email is listed in test users
   - Remove and re-add if needed
   - Wait a few seconds for changes to propagate

3. **For Production Use:**
   - Submit app for Google verification
   - Complete verification process
   - App will be available to all users

## MCP Server Issues

### Error: "No server info found" or Server Not Loading

**Symptoms:**
- MCP tools not available in Cursor
- Server not appearing in Cursor's MCP server list

**Causes:**
- MCP configuration incorrect
- Server path incorrect
- Python environment not found
- Server failing to start

**Solutions:**

1. **Verify MCP Configuration:**
   ```json
   {
     "mcpServers": {
       "google-services": {
         "command": "python",
         "args": [
           "-m",
           "mcp_google_services.server"
         ],
         "cwd": "/absolute/path/to/mcp-google-services"
       }
     }
   }
   ```

2. **Check Python Path:**
   ```bash
   # Verify Python is in PATH
   which python
   python --version
   
   # Use full Python path in MCP config if needed
   ```

3. **Restart Cursor:**
   - Completely quit Cursor (not just close window)
   - Reopen Cursor
   - Check MCP server status

4. **Check Server Logs:**
   - Look for errors in Cursor's MCP logs
   - Check terminal output if running server manually

### Server Loads Multiple Times

**Symptoms:**
- Server appears to load 4+ times in Cursor
- Multiple initialization messages

**Cause:**
- Normal behavior during development
- Cursor may retry initialization

**Solution:**
- This is expected behavior
- Server should stabilize after a few seconds
- If it doesn't stabilize, check for errors in logs

## Gmail API Issues

### Error: "Rate limit exceeded" (429)

**Symptoms:**
- API calls fail with 429 errors
- "Quota exceeded" messages

**Causes:**
- Too many API requests
- Exceeding quota per second limit
- Daily quota exhausted

**Solutions:**

1. **Wait and Retry:**
   - Rate limiter automatically handles retries
   - Wait a few seconds and try again

2. **Reduce Request Rate:**
   - Use smaller batch sizes
   - Reduce `max_results` parameter
   - Add delays between operations

3. **Check Quota Usage:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Navigate to "APIs & Services" > "Quotas"
   - Check Gmail API quota usage

### Error: "Message not found" (404)

**Symptoms:**
- Individual message retrieval fails
- 404 errors for specific messages

**Causes:**
- Message deleted from Gmail
- Message ID invalid
- Message not accessible

**Solutions:**

1. **Skip and Continue:**
   - Backup system automatically skips failed messages
   - Check `messages_failed` count in result

2. **Verify Message ID:**
   - Check if message exists in Gmail
   - Verify message ID is correct

3. **Retry Operation:**
   - Message may be temporarily unavailable
   - Retry the operation

### Error: "Metadata scope does not support 'q' parameter"

**Symptoms:**
- Search queries fail
- Error about metadata scope

**Causes:**
- Using `gmail.metadata` scope which doesn't support queries
- Need `gmail.readonly` scope for search

**Solutions:**

1. **Use Readonly Scope:**
   - Server automatically uses `gmail.readonly` scope
   - Ensure OAuth credentials request this scope

2. **Verify Scope in Credentials:**
   - Check token has `gmail.readonly` scope
   - Re-authenticate if needed

## Backup Issues

### Backup Returns Zero Messages

**Symptoms:**
- Backup completes successfully but no messages
- `message_count: 0` in result

**Causes:**
- No new messages since last backup (incremental)
- Query filter too restrictive
- Date filter excludes all messages

**Solutions:**

1. **Check Last Backup Time:**
   ```python
   # Check backup state
   cat backups/gmail/backup_state.json
   ```

2. **Verify Query:**
   - Test query in Gmail web interface
   - Remove restrictive filters
   - Use full backup to verify

3. **Check Date Filter:**
   - Incremental backup uses date filter
   - Verify date format: `YYYY/MM/DD`

### Backup File Empty or Corrupted

**Symptoms:**
- MBOX file exists but is empty
- Cannot import MBOX file
- File size is 0 bytes

**Causes:**
- Backup interrupted
- Disk space exhausted
- Permission errors

**Solutions:**

1. **Check File Size:**
   ```bash
   ls -lh backups/gmail/gmail_backup_*.mbox
   ```

2. **Verify File Format:**
   ```bash
   # Check if file has "From " lines
   grep -c "^From " backups/gmail/gmail_backup_*.mbox
   ```

3. **Retry Backup:**
   - Delete corrupted backup file
   - Run backup again
   - Check for sufficient disk space

4. **Check Permissions:**
   ```bash
   # Ensure backup directory is writable
   chmod 755 backups/gmail
   ```

### Messages Not Appearing in Backup

**Symptoms:**
- Expected messages missing from backup
- Backup count lower than expected

**Causes:**
- Query filter excludes messages
- Date filter too restrictive
- Messages deleted from Gmail
- Messages in excluded labels

**Solutions:**

1. **Check Query:**
   - Verify query syntax
   - Test query in Gmail web interface
   - Remove restrictive filters

2. **Verify Date Filter:**
   - Check last backup timestamp
   - Adjust date filter if needed

3. **Perform Full Backup:**
   - Use full backup to verify all messages
   - Compare with incremental backup

## Export Issues

### Export Format Not Supported

**Symptoms:**
- Error about unsupported format
- Export fails

**Causes:**
- Invalid format specified
- Format not implemented

**Solutions:**

1. **Check Supported Formats:**
   - MBOX: ✅ Supported
   - JSON: ✅ Supported
   - CSV: ✅ Supported
   - EML: ✅ Supported

2. **Use Valid Format:**
   ```json
   {
     "format": "json"  // or "mbox", "csv", "eml"
   }
   ```

### Export File Too Large

**Symptoms:**
- Export completes but file is very large
- Memory issues during export

**Causes:**
- Too many messages exported
- Large attachments included

**Solutions:**

1. **Limit Messages:**
   ```json
   {
     "max_results": 100  // Limit number of messages
   }
   ```

2. **Use Query Filter:**
   ```json
   {
     "query": "newer_than:30d"  // Export only recent messages
   }
   ```

3. **Export in Batches:**
   - Export messages in smaller batches
   - Combine results if needed

## Performance Issues

### Backup Takes Too Long

**Symptoms:**
- Backup process very slow
- Timeout errors

**Causes:**
- Too many messages
- Slow API responses
- Rate limiting delays

**Solutions:**

1. **Use Incremental Backup:**
   - Only backup new messages
   - Faster than full backup

2. **Reduce Message Count:**
   ```json
   {
     "max_results": 500  // Limit messages per backup
   }
   ```

3. **Use Query Filter:**
   ```json
   {
     "query": "newer_than:7d"  // Only recent messages
   }
   ```

4. **Check API Performance:**
   - Verify network connection
   - Check Google API status
   - Monitor rate limiting

### High Memory Usage

**Symptoms:**
- System becomes slow
- Out of memory errors

**Causes:**
- Processing too many messages at once
- Large attachments
- Memory leaks

**Solutions:**

1. **Process in Batches:**
   - Use smaller batch sizes
   - Process messages incrementally

2. **Limit Attachments:**
   - Exclude large attachments
   - Use query to filter messages

3. **Monitor Memory:**
   - Check system memory usage
   - Reduce concurrent operations

## Getting Help

### Debug Information

When reporting issues, include:

1. **Error Messages:**
   - Full error text
   - Stack traces (if available)

2. **Configuration:**
   - Python version: `python --version`
   - MCP server version
   - Configuration file (sanitized)

3. **Environment:**
   - Operating system
   - Cursor version
   - MCP configuration

4. **Logs:**
   - Cursor MCP logs
   - Server output
   - Backup state file

### Support Channels

- **GitHub Issues**: [Create an issue](https://github.com/CloudBoostUP/mcp-google-services/issues)
- **Documentation**: Check [README.md](../README.md)
- **Email**: support@cloudboostup.com

## Common Solutions Summary

| Issue | Quick Fix |
|-------|-----------|
| Authentication error | Set up OAuth credentials file (required for Gmail API) |
| Server not loading | Check MCP configuration and restart Cursor |
| Rate limit exceeded | Wait and retry, or reduce request rate |
| No messages in backup | Check query filter and last backup time |
| Backup file corrupted | Delete file and retry backup |
| Export format error | Use supported format: mbox, json, csv, eml |

