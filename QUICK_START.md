# Quick Start - Google Services MCP Server

## 🚀 Setup Steps

### Step 1: Create OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Create OAuth client ID (Desktop app)
3. Download JSON file
4. Place in `config/credentials.json`

### Step 2: Enable Gmail API

1. Go to [Google Cloud Console - APIs Library](https://console.cloud.google.com/apis/library)
2. Search for "Gmail API"
3. Click "Enable"

### Step 3: Configure OAuth Consent Screen

1. Go to [OAuth Consent Screen](https://console.cloud.google.com/apis/credentials/consent)
2. Add your Gmail address as a test user (required!)
3. Add scope: `https://www.googleapis.com/auth/gmail.readonly`

### Step 4: Use in Cursor

Just ask Cursor:
- "List my Gmail labels"
- "List my Gmail messages"  
- "Backup my Gmail messages"
- "Export my Gmail to JSON"

On first use, the browser will open for OAuth consent.

## ✅ That's It!

After first-time OAuth consent, credentials are stored securely and you won't need to authenticate again.

## 📚 For Detailed Instructions

See [docs/AUTHENTICATION.md](docs/AUTHENTICATION.md) for complete setup guide.

