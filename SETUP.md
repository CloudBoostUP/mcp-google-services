# Setup Guide - Google Services MCP Server

> **⚠️ This file is deprecated. Please refer to the main documentation for the most up-to-date setup instructions.**

## 📚 Current Documentation

For setup instructions, please see:

- **[README.md](README.md)** - Quick start guide with installation and authentication
- **[docs/AUTHENTICATION.md](docs/AUTHENTICATION.md)** - Detailed authentication setup guide
- **[docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)** - Common issues and solutions

## Quick Reference

### Gmail API Setup

**Important:** Gmail API requires OAuth 2.0 credentials file. `gcloud auth application-default login` does not support Gmail scopes.

1. **Download OAuth 2.0 credentials** from [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. **Place credentials** in `config/credentials.json`
3. **Enable Gmail API** in your Google Cloud project
4. **First use** will prompt for OAuth consent

See [docs/AUTHENTICATION.md](docs/AUTHENTICATION.md) for detailed instructions.

## Why This File Exists

This file is kept for historical reference. The setup process has been updated and consolidated into the main documentation files listed above.

