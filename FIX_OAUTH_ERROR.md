# Fix: "access_denied" Error - OAuth Consent Screen

## Problem

You're seeing this error:
```
Error 403: access_denied
Gmail MCP Server has not completed the Google verification process.
```

## Solution: Add Yourself as a Test User

Your OAuth consent screen is in **"Testing"** mode, which means only approved test users can access it.

### Quick Fix (2 minutes)

1. **Go to Google Cloud Console:**
   - Open: https://console.cloud.google.com/apis/credentials/consent

2. **Add Test Users:**
   - Scroll down to **"Test users"** section
   - Click **"+ ADD USERS"**
   - Enter your Gmail address (the one you want to use)
   - Click **"ADD"**

3. **Try Again:**
   - Go back to Cursor and try: "List my Gmail labels"
   - The browser will open again
   - This time it should work! ✅

## Alternative: Publish Your App (For Production)

If you want to make it available to anyone (or just yourself without test user restrictions):

1. **Go to OAuth Consent Screen:**
   - https://console.cloud.google.com/apis/credentials/consent

2. **Publish Your App:**
   - Click **"PUBLISH APP"** button
   - Confirm the warning (this makes it available to all users)
   - Note: You'll need to provide privacy policy and terms of service URLs for production apps

3. **For Personal Use:**
   - You can keep it in Testing mode and just add yourself as a test user (easier!)

## Why This Happens

Google requires apps to be either:
- **Testing mode**: Only approved test users can access (recommended for personal use)
- **Production mode**: Available to all users (requires verification for sensitive scopes like Gmail)

For personal use, **Testing mode + test user** is the simplest approach.

