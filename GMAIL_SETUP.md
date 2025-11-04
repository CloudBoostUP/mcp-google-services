# Gmail API Setup Guide

## Important: Gmail API Requires OAuth Credentials

The `gcloud auth application-default login` command provides credentials for Google Cloud Platform services, but **does not include Gmail API scopes** by default.

For Gmail API access, you need to set up OAuth 2.0 credentials.

## Quick Setup (5 minutes)

### Step 1: Create OAuth Credentials in Google Cloud Console

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select or create a project
3. Navigate to **APIs & Services** > **Credentials**
4. Click **+ CREATE CREDENTIALS** > **OAuth client ID**
5. If prompted, configure the OAuth consent screen:
   - Choose **External** user type
   - Fill in required fields (app name, user support email, etc.)
   - Add scopes: `https://www.googleapis.com/auth/gmail.readonly`
   - Add your email as a test user
6. Back in Credentials:
   - Choose **Desktop app** as application type
   - Click **CREATE**
7. Download the JSON file (it will be named something like `client_secret_XXXXX.json`)

### Step 2: Place Credentials File

```bash
# Create config directory if it doesn't exist
mkdir -p config

# Copy downloaded file to config/credentials.json
cp ~/Downloads/client_secret_*.json config/credentials.json
```

### Step 3: Test Authentication

The MCP server will automatically:
1. Detect the credentials file
2. Open your browser for authentication
3. Request Gmail API permissions
4. Store credentials securely

When you first use the MCP server (e.g., "List my Gmail labels"), it will prompt you to authenticate.

## Alternative: Using Existing gcloud Auth

If you want to use `gcloud auth` for other services but need OAuth for Gmail:

1. The MCP server will automatically use OAuth credentials when available
2. You can have both: `gcloud auth` for Cloud Platform, OAuth for Gmail API
3. The server prioritizes OAuth credentials for Gmail operations

## Troubleshooting

### "Insufficient authentication scopes"

This means your credentials don't have Gmail API scopes. Set up OAuth credentials as described above.

### "API not enabled"

Enable Gmail API in Google Cloud Console:
1. Go to **APIs & Services** > **Library**
2. Search for "Gmail API"
3. Click **Enable**

### "OAuth consent screen not configured"

Follow Step 1 above to configure the OAuth consent screen.

