# Authentication Guide - Google Services MCP Server

## Overview

The Google Services MCP Server requires OAuth 2.0 authentication for Gmail API access. This guide explains how to set up authentication.

## Gmail API Authentication

**Important:** Gmail API requires OAuth 2.0 credentials file. `gcloud auth application-default login` does not support Gmail scopes and cannot be used for Gmail API access.

### Step 1: Create OAuth 2.0 Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable **Gmail API**:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Gmail API"
   - Click "Enable"
4. Create OAuth 2.0 Credentials:
   - Navigate to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Desktop app" as application type
   - Download the JSON file

### Step 2: Configure OAuth Consent Screen

1. Navigate to "APIs & Services" > "OAuth consent screen"
2. Fill in required information:
   - User type: External (for personal use) or Internal (for Google Workspace)
   - App name: e.g., "Gmail MCP Server"
   - User support email: Your email
   - Developer contact: Your email
3. Add scopes:
   - `https://www.googleapis.com/auth/gmail.readonly` (for reading emails)
   - `https://www.googleapis.com/auth/gmail.send` (for sending emails)
4. Add test users (if app is in "Testing" mode):
   - Scroll to "Test users" section
   - Click "+ ADD USERS"
   - Enter your Gmail address
   - Click "ADD"
   - **Important**: This step is required for apps in "Testing" mode

### Step 3: Place Credentials File

Place the downloaded OAuth credentials JSON file in the project:

```bash
mkdir -p config
cp ~/Downloads/your-credentials.json config/credentials.json
```

**Security Note:** Never commit `config/credentials.json` to git. It's already in `.gitignore`.

### Step 4: First-Time Authentication

On first use, the MCP server will:
1. Detect the OAuth credentials file
2. Open your browser automatically
3. Prompt for Google account sign-in
4. Request Gmail API permissions
5. Store tokens securely (using keyring)

You only need to do this once - tokens are stored and automatically refreshed.

## Authentication Methods

### Primary: OAuth Credentials File (Required for Gmail)

This is the **only** method that works for Gmail API:

1. Download OAuth 2.0 credentials from Google Cloud Console
2. Place in `config/credentials.json`
3. First use will prompt for OAuth consent
4. Tokens stored securely using keyring

### Application Default Credentials (ADC)

**Note:** `gcloud auth application-default login` does **NOT** work for Gmail API because it doesn't support Gmail scopes. ADC can be used for other Google services, but Gmail requires OAuth credentials file.

## Token Management

### Automatic Token Refresh

- Tokens are automatically refreshed when expired
- No manual intervention needed
- Stored securely in system keyring

### Switching Accounts

To use a different Google account:

1. Delete stored tokens:
   ```bash
   # Tokens are stored in keyring, or:
   rm config/tokens.json  # if file-based storage is used
   ```
2. Re-authenticate on next use

## Troubleshooting

### "No authentication credentials found"

**Solution**: 
- Ensure `config/credentials.json` exists with valid OAuth credentials
- Download OAuth credentials from Google Cloud Console

### "Gmail API scopes are required but not present"

**Solution**: 
- Gmail API requires OAuth credentials file
- `gcloud auth application-default login` does not support Gmail scopes
- Use OAuth credentials file method (see Step 1-4 above)

### "Permission denied" or "403 Forbidden"

**Solutions**:
1. **Enable Gmail API** in Google Cloud Console
2. **Configure OAuth Consent Screen** with Gmail scopes
3. **Add Test Users** (if app is in "Testing" mode)
4. **Re-authenticate** after making changes

### "gcloud: command not found"

**Solution**: 
- Install Google Cloud SDK (optional, not required for Gmail API)
- Gmail API requires OAuth credentials file, not gcloud

## Security Notes

- OAuth credentials are stored locally in `config/credentials.json` (not in git)
- Tokens are stored securely using system keyring
- Tokens are automatically refreshed when expired
- Each user's credentials are isolated
- Never commit credentials files to version control

## Quick Reference

**For Gmail API:**
- ✅ OAuth 2.0 credentials file (required)
- ❌ `gcloud auth application-default login` (does not support Gmail scopes)

**Setup Steps:**
1. Enable Gmail API in Google Cloud Console
2. Create OAuth 2.0 credentials (Desktop app)
3. Configure OAuth consent screen
4. Place credentials in `config/credentials.json`
5. First use will prompt for OAuth consent

