# Google Services MCP Server

A Model Context Protocol (MCP) server for automated Gmail backup and Google services management. This server provides scalable, automated email backup without manual Google Takeout processes.

## 🎯 Purpose

This MCP server enables:
- **Automated Gmail Backup**: Scheduled email backup using Gmail API
- **MBOX Export**: Export emails in standard MBOX format for portability
- **Multiple Export Formats**: JSON, CSV, EML, and MBOX support
- **Incremental Backup**: Only backup new/changed emails since last backup
- **Google Services Integration**: Extensible framework for future Google services

## 🚀 Features

### Currently Implemented (Gmail)

- ✅ **Gmail API Integration**: Direct access to Gmail messages and metadata
- ✅ **Automated Backup**: Full and incremental backup support
- ✅ **MBOX Format Export**: RFC 4155 compliant MBOX file generation
- ✅ **Multiple Export Formats**: MBOX, JSON, CSV, EML
- ✅ **Label Management**: List and filter by Gmail labels
- ✅ **Message Search**: Query messages with Gmail search syntax
- ✅ **Rate Limiting**: Intelligent API quota management
- ✅ **Authentication**: OAuth 2.0 with Application Default Credentials support

### Planned Features

- 📅 **Scheduling System**: Automated backup scheduling (cron-based)
- 🔄 **Additional Google Services**: Drive, Calendar, Sheets, Docs, Photos, Contacts
- 📊 **Progress Tracking**: Real-time backup progress monitoring
- 🔒 **Compression**: Optional backup compression for storage efficiency
- 🔐 **Encryption**: Optional encryption for sensitive data

## 📋 Prerequisites

- Python 3.8 or higher
- Google Cloud Project with Gmail API enabled
- OAuth 2.0 credentials (for Gmail API access)
- Required Python packages (see `requirements.txt`)

## 🛠️ Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/CloudBoostUP/mcp-google-services.git
cd mcp-google-services
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Google API Credentials

**Gmail API requires OAuth 2.0 credentials file.** `gcloud auth application-default login` does not support Gmail scopes and cannot be used for Gmail API access.

#### OAuth 2.0 Credentials File (Required)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable **Gmail API**:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Gmail API"
   - Click "Enable"
4. Create OAuth 2.0 Credentials:
   - Navigate to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Desktop app" as application type
   - Download the JSON file
5. Place credentials in `config/credentials.json`:
   ```bash
   mkdir -p config
   cp ~/Downloads/your-credentials.json config/credentials.json
   ```

### 4. Configure MCP Server in Cursor

Add to your Cursor MCP configuration (`~/.cursor/mcp.json` or `.vscode/mcp.json`):

```json
{
  "mcpServers": {
    "google-services": {
      "command": "python",
      "args": [
        "-m",
        "mcp_google_services.server"
      ],
      "cwd": "/path/to/mcp-google-services"
    }
  }
}
```

Restart Cursor to load the MCP server.

## 🚀 Usage

### Using MCP Tools in Cursor

Once the server is configured, you can use natural language commands:

#### List Gmail Labels
```
"List my Gmail labels"
"Show me all Gmail labels"
```

#### List Gmail Messages
```
"List my Gmail messages"
"Show me recent emails from last week"
"List messages from sender@example.com"
"Find emails with attachments"
```

#### Backup Gmail Messages
```
"Backup my Gmail messages"
"Create a full backup of my Gmail"
"Do an incremental backup of my emails"
"Backup messages from the last month"
```

#### Export Gmail Messages
```
"Export my Gmail to JSON"
"Export my emails to CSV format"
"Export recent messages to MBOX"
```

### MCP Tool Reference

#### `gmail_list_labels`
List all Gmail labels for a user.

**Parameters:**
- `user_id` (string, optional): Gmail user ID (default: "me")

**Example:**
```json
{
  "tool": "gmail_list_labels",
  "arguments": {
    "user_id": "me"
  }
}
```

#### `gmail_list_messages`
List Gmail messages with optional filtering.

**Parameters:**
- `user_id` (string, optional): Gmail user ID (default: "me")
- `query` (string, optional): Gmail search query (e.g., "from:example@gmail.com", "has:attachment")
- `max_results` (integer, optional): Maximum number of messages (default: 10)

**Example:**
```json
{
  "tool": "gmail_list_messages",
  "arguments": {
    "user_id": "me",
    "query": "from:example@gmail.com newer_than:7d",
    "max_results": 20
  }
}
```

#### `gmail_backup`
Backup Gmail messages to MBOX format.

**Parameters:**
- `user_id` (string, optional): Gmail user ID (default: "me")
- `backup_type` (string, optional): "incremental" or "full" (default: "incremental")
- `max_results` (integer, optional): Maximum number of messages (default: 1000)
- `query` (string, optional): Gmail search query to filter messages

**Example:**
```json
{
  "tool": "gmail_backup",
  "arguments": {
    "user_id": "me",
    "backup_type": "incremental",
    "max_results": 1000
  }
}
```

#### `gmail_export`
Export Gmail messages to various formats.

**Parameters:**
- `user_id` (string, optional): Gmail user ID (default: "me")
- `format` (string, optional): Export format - "mbox", "json", "csv", "eml" (default: "mbox")
- `output_path` (string, optional): Output file path (auto-generated if not provided)
- `max_results` (integer, optional): Maximum number of messages (default: 100)
- `query` (string, optional): Gmail search query to filter messages

**Example:**
```json
{
  "tool": "gmail_export",
  "arguments": {
    "user_id": "me",
    "format": "json",
    "max_results": 100
  }
}
```

## 📁 Project Structure

```
mcp-google-services/
├── src/
│   └── mcp_google_services/
│       ├── server.py              # MCP server implementation
│       ├── core/
│       │   ├── auth.py            # OAuth 2.0 authentication
│       │   ├── client.py          # Google API client base
│       │   ├── rate_limiter.py    # API quota management
│       │   └── scheduler.py      # Backup scheduling (planned)
│       ├── services/
│       │   └── gmail/
│       │       ├── api.py         # Gmail API client
│       │       ├── backup.py     # Backup operations
│       │       ├── export.py     # Export operations
│       │       ├── mbox.py        # MBOX format generation
│       │       └── parser.py     # Email parsing
│       └── utils/
│           └── config.py          # Configuration management
├── config/
│   ├── config.example.json        # Example configuration
│   └── credentials.json           # Google API credentials (not in git)
├── backups/
│   └── gmail/                     # Backup files (MBOX format)
├── exports/
│   └── gmail/                     # Export files (various formats)
├── docs/
│   ├── AUTHENTICATION.md          # Authentication setup guide
│   ├── architecture/              # Architecture documentation
│   └── specifications/             # Technical specifications
├── tests/                         # Test suite
├── requirements.txt               # Python dependencies
├── pyproject.toml                 # Project configuration
├── README.md                      # This file
└── CONTRIBUTING.md                # Contribution guidelines
```

## 🔧 Configuration

### Configuration File

Create `config/config.json` from the example:

```bash
cp config/config.example.json config/config.json
```

Example configuration:

```json
{
  "google_apis": {
    "credentials_path": "config/credentials.json"
  },
  "services": {
    "gmail": {
      "backup_folder": "backups/gmail",
      "max_messages_per_batch": 100
    }
  }
}
```

### Environment Variables

```bash
export GOOGLE_APPLICATION_CREDENTIALS="path/to/credentials.json"
export MCP_GMAIL__BACKUP_FOLDER="backups/gmail"
```

## 📚 Documentation

- [**Authentication Guide**](docs/AUTHENTICATION.md) - Detailed authentication setup
- [**Usage Guide**](USAGE.md) - How to use MCP tools in Cursor
- [**Gmail API Integration**](docs/services/GMAIL_API.md) - Gmail API integration details
- [**MBOX Generation Process**](docs/services/MBOX_GENERATION.md) - How MBOX files are created
- [**Backup System**](docs/services/BACKUP_SYSTEM.md) - Incremental vs full backup explained
- [**Troubleshooting Guide**](docs/TROUBLESHOOTING.md) - Common issues and solutions
- [**Architecture Documentation**](docs/architecture/) - System architecture and design
- [**Technical Specifications**](docs/specifications/) - Detailed technical specs

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific test suite
pytest tests/test_services/test_gmail_integration.py

# Run with coverage
pytest --cov=mcp_google_services
```

## 🚨 Troubleshooting

### Authentication Issues

**Error: "No authentication credentials found"**
- **Solution**: Set up OAuth credentials file (required for Gmail API)

**Error: "Gmail API scopes are required but not present"**
- **Solution**: Download OAuth 2.0 credentials from Google Cloud Console and place in `config/credentials.json`

**Error: "Permission denied"**
- **Solution**: Ensure Gmail API is enabled in your Google Cloud project

See [Troubleshooting Guide](docs/TROUBLESHOOTING.md) for more details.

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run linting
flake8 src/
black src/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [GitHub Wiki](https://github.com/CloudBoostUP/mcp-google-services/wiki)
- **Issues**: [GitHub Issues](https://github.com/CloudBoostUP/mcp-google-services/issues)
- **Email**: support@cloudboostup.com
- **Website**: [cloudboostup.com](https://cloudboostup.com)

## 🙏 Acknowledgments

- Google API teams for excellent API documentation
- Model Context Protocol community for MCP framework
- CloudBoostUP team for project development

---

**Made with ❤️ by CloudBoostUP**

[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/CloudBoostUP/mcp-google-services/blob/main/CONTRIBUTING.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
