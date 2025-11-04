# How to Run the OAuth Setup Script

## Quick Start

Since you already have the credentials file, you can skip directly to adding yourself as a test user.

### Option 1: Run the Full Setup Script (Recommended for First Time)

```bash
cd /Users/adriankomorek/git/github/CloudBoostUP/mcp-google-services
source .venv/bin/activate
python setup_oauth.py
```

The script will:
- Guide you through each step
- Open browser windows automatically
- Help you place the credentials file
- **Remind you to add yourself as a test user**

### Option 2: Quick Fix - Just Add Test User (If Credentials Already Set Up)

Since you already have `config/credentials.json`, you just need to:

1. **Open OAuth Consent Screen:**
   ```bash
   # Or just open this URL in your browser:
   open "https://console.cloud.google.com/apis/credentials/consent"
   ```

2. **Add Yourself as Test User:**
   - Scroll down to "Test users" section
   - Click "+ ADD USERS"
   - Enter your Gmail address
   - Click "ADD"

3. **Test in Cursor:**
   - Try: "List my Gmail labels"
   - Browser will open for authentication
   - Should work now! ✅

### Option 3: Manual Setup (If Script Doesn't Work)

If the interactive script doesn't work, follow these steps manually:

1. **Enable Gmail API:**
   - https://console.cloud.google.com/apis/library/gmail.googleapis.com
   - Click "Enable"

2. **Configure OAuth Consent Screen:**
   - https://console.cloud.google.com/apis/credentials/consent
   - Add your Gmail address as a test user (CRITICAL!)

3. **Verify Credentials File:**
   ```bash
   ls -la config/credentials.json
   ```
   Should show your credentials file exists.

4. **Test Authentication:**
   ```bash
   python test_auth.py
   ```

## Troubleshooting

### "EOF when reading a line"
The script is interactive and needs to be run in your terminal, not through automation.

### "File not found"
The script will automatically search for credential files in your Downloads folder.

### "access_denied" Error
You MUST add yourself as a test user in the OAuth consent screen!

