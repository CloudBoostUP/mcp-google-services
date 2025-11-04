# Authentication Guide - Google Services MCP Server

## Quick Setup (Similar to `az login`)

The easiest way to authenticate is using **Google Cloud SDK**, similar to how Azure DevOps uses `az login`:

### Step 1: Install Google Cloud SDK

**macOS:**
```bash
brew install google-cloud-sdk
```

**Windows:**
```powershell
# Download from: https://cloud.google.com/sdk/docs/install
```

**Linux:**
```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

### Step 2: Authenticate (One-time setup)

```bash
gcloud auth application-default login
```

This will:
- Open your browser
- Ask you to sign in with your Google account
- Grant permissions for Gmail API
- Store credentials locally (no manual file management needed!)

### Step 3: Verify Authentication

```bash
gcloud auth application-default print-access-token
```

If you see a token, authentication is working!

## How It Works

The MCP server automatically uses **Application Default Credentials (ADC)** when available, which means:

✅ **No credentials file needed** - Just run `gcloud auth application-default login` once  
✅ **Automatic token refresh** - Credentials are managed by Google Cloud SDK  
✅ **Same workflow as Azure DevOps** - Simple CLI command, no manual file handling  
✅ **Secure** - Credentials stored in your system keyring  

## Alternative: OAuth Credentials File

If you prefer not to use Google Cloud SDK, you can use OAuth credentials file:

1. Download OAuth 2.0 credentials from Google Cloud Console
2. Place in `config/credentials.json`
3. The server will prompt for OAuth consent on first use

## Switching Accounts

To switch Google accounts:

```bash
gcloud auth application-default login
```

This will prompt for a new account login.

## Troubleshooting

### "No authentication credentials found"

**Solution**: Run `gcloud auth application-default login`

### "gcloud: command not found"

**Solution**: Install Google Cloud SDK (see Step 1 above)

### "Permission denied" errors

**Solution**: Ensure Gmail API is enabled in your Google Cloud project and you've granted the necessary scopes.

## Security Notes

- Application Default Credentials are stored securely in your system keyring
- Tokens are automatically refreshed when expired
- No credentials files need to be committed to git
- Each user's credentials are isolated

