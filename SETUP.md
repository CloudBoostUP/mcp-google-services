# Quick Setup Guide - Google Services MCP Server

## One-Time Authentication Setup

### Step 1: Authenticate with Google (Similar to `az login`)

Run this command in your terminal:

```bash
gcloud auth application-default login
```

This will:
- Open your browser automatically
- Ask you to sign in with your Google account
- Grant permissions for Gmail API access
- Store credentials securely (no file management needed!)

### Step 2: Verify Authentication

Test that authentication worked:

```bash
gcloud auth application-default print-access-token
```

If you see a token, you're ready to go!

### Step 3: Test in Cursor

Now you can use the MCP server in Cursor:

- "List my Gmail labels"
- "List my Gmail messages"
- "Backup my Gmail messages"
- "Export my Gmail to JSON"

## That's It!

No credentials files to manage, no manual token handling. Just like `az login` for Azure DevOps or AWS CLI profiles.

The MCP server will automatically use your Google Cloud SDK credentials.

## Troubleshooting

### "gcloud: command not found"

Google Cloud SDK is installed but not in PATH. Add to your shell profile:

```bash
# For zsh
echo 'export PATH=/opt/homebrew/share/google-cloud-sdk/bin:$PATH' >> ~/.zshrc
source ~/.zshrc

# For bash
echo 'export PATH=/opt/homebrew/share/google-cloud-sdk/bin:$PATH' >> ~/.bash_profile
source ~/.bash_profile
```

### "Permission denied" or "API not enabled"

1. Enable Gmail API in Google Cloud Console:
   - Go to https://console.cloud.google.com/
   - Navigate to APIs & Services > Library
   - Search for "Gmail API"
   - Click "Enable"

2. Re-authenticate:
   ```bash
   gcloud auth application-default login
   ```

### Switching Accounts

To use a different Google account:

```bash
gcloud auth application-default login
```

This will prompt for a new account login.

