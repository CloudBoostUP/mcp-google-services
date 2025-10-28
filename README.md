# Google MCP Server

A Model Context Protocol (MCP) server for automated Gmail backup and Google services management. This server provides scalable, automated email backup without manual Google Takeout processes.

## 🎯 Purpose

This MCP server enables:
- **Automated Gmail Backup**: Scheduled email backup using Gmail API
- **GMail BOX Export**: Export emails in standard MBOX format
- **Google Services Integration**: Extensible framework for other Google services
- **Scheduling System**: Automated backup scheduling and management
- **Data Portability**: Leverage Google Data Portability API for comprehensive data export

## 🚀 Features

### Core Functionality
- **Gmail API Integration**: Direct access to Gmail messages and metadata
- **Automated Backup**: Scheduled email backup without manual intervention
- **GMail BOX Export**: Standard email format for portability
- **Incremental Backup**: Only backup new/changed emails
- **Metadata Preservation**: Maintain email headers, labels, and timestamps

### Advanced Features
- **Scheduling System**: Flexible backup scheduling (daily, weekly, custom)
- **Error Handling**: Robust error handling and retry mechanisms
- **Progress Tracking**: Real-time backup progress monitoring
- **Compression**: Optional backup compression for storage efficiency
- **Encryption**: Optional encryption for sensitive data

## 📋 Prerequisites

- Python 3.8 or higher
- Google Cloud Project with Gmail API enabled
- Service account credentials or OAuth2 setup
- Required Python packages (see requirements.txt)

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone https://github.com/CloudBoostUP/mcp-google-services.git
cd mcp-google-services
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Google API Setup
1. Create a Google Cloud Project
2. Enable Gmail API
3. Create service account credentials
4. Download credentials JSON file
5. Place credentials in `config/credentials.json`

### 4. Configuration
```bash
cp config/config.example.json config/config.json
# Edit config.json with your settings
```

## 🔧 Configuration

### Environment Variables
```bash
export GOOGLE_APPLICATION_CREDENTIALS="path/to/credentials.json"
export MCP_SERVER_PORT=3000
export BACKUP_SCHEDULE="0 2 * * *"  # Daily at 2 AM
```

### Configuration File (config/config.json)
```json
{
  "gmail": {
    "credentials_path": "config/credentials.json",
    "backup_folder": "backups",
    "max_messages_per_request": 100,
    "include_labels": ["INBOX", "SENT"],
    "exclude_labels": ["SPAM", "TRASH"]
  },
  "schedule": {
    "enabled": true,
    "cron_expression": "0 2 * * *",
    "timezone": "UTC"
  },
  "export": {
    "format": "mbox",
    "compression": true,
    "encryption": false
  }
}
```

## 🚀 Usage

### Start the MCP Server
```bash
python -m mcp_google_services.server
```

### Manual Backup
```bash
python -m mcp_google_services.backup --user-id="user@example.com"
```

### Schedule Management
```bash
# Enable scheduling
python -m mcp_google_services.scheduler --enable

# Disable scheduling
python -m mcp_google_services.scheduler --disable

# Check status
python -m mcp_google_services.scheduler --status
```

## 📊 API Endpoints

### MCP Tools
- `gmail_backup`: Initiate Gmail backup
- `gmail_status`: Check backup status
- `gmail_schedule`: Manage backup scheduling
- `gmail_export`: Export backup data
- `gmail_restore`: Restore from backup

### Example MCP Tool Usage
```json
{
  "tool": "gmail_backup",
  "arguments": {
    "user_id": "user@example.com",
    "labels": ["INBOX", "SENT"],
    "date_range": "2024-01-01:2024-12-31"
  }
}
```

## 📁 Project Structure

```
mcp-google-services/
├── src/
│   ├── mcp_google_services/
│   │   ├── server.py              # MCP server implementation
│   │   ├── gmail/
│   │   │   ├── api.py             # Gmail API client
│   │   │   ├── backup.py          # Backup functionality
│   │   │   └── export.py          # Export utilities
│   │   ├── scheduler/
│   │   │   ├── cron.py            # Cron job management
│   │   │   └── tasks.py           # Scheduled tasks
│   │   └── utils/
│   │       ├── config.py          # Configuration management
│   │       └── logging.py         # Logging utilities
├── config/
│   ├── config.example.json        # Example configuration
│   └── credentials.json           # Google API credentials
├── tests/
│   ├── test_gmail_api.py          # Gmail API tests
│   ├── test_backup.py             # Backup functionality tests
│   └── test_scheduler.py          # Scheduler tests
├── docs/
│   ├── api.md                     # API documentation
│   ├── setup.md                   # Setup guide
│   └── troubleshooting.md         # Troubleshooting guide
├── requirements.txt               # Python dependencies
├── pyproject.toml                 # Project configuration
└── README.md                      # This file
```

# Google Services MCP Server

A comprehensive Model Context Protocol (MCP) server for Google services integration and automation. This server provides a unified interface for interacting with various Google APIs and services through the Model Context Protocol.

## 🎯 Purpose

This MCP server enables:
- **Multi-Service Integration**: Unified access to Google APIs (Gmail, Drive, Calendar, Sheets, etc.)
- **Automated Data Management**: Scheduled backups, exports, and data processing
- **Service Orchestration**: Coordinate operations across multiple Google services
- **Data Portability**: Leverage Google Data Portability API for comprehensive data export
- **Custom Workflows**: Build automated workflows using Google services

## 🚀 Features

### Core Functionality
- **Gmail Integration**: Email backup, management, and automation
- **Google Drive**: File management, backup, and synchronization
- **Google Calendar**: Event management and scheduling
- **Google Sheets**: Spreadsheet operations and data processing
- **Google Docs**: Document management and processing
- **Google Photos**: Photo backup and organization
- **Google Contacts**: Contact management and synchronization

### Advanced Features
- **Service Orchestration**: Coordinate operations across multiple services
- **Scheduling System**: Flexible automation scheduling (cron-based)
- **Error Handling**: Robust error handling and retry mechanisms
- **Progress Tracking**: Real-time operation progress monitoring
- **Data Export**: Multiple export formats (JSON, CSV, MBOX, etc.)
- **Authentication Management**: Unified OAuth2 and service account handling
- **Rate Limiting**: Intelligent API quota management

## 📋 Prerequisites

- Python 3.8 or higher
- Google Cloud Project with required APIs enabled
- Service account credentials or OAuth2 setup
- Required Python packages (see requirements.txt)

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone https://github.com/CloudBoostUP/mcp-google-services.git
cd mcp-google-services
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Google API Setup
1. Create a Google Cloud Project
2. Enable required Google APIs:
   - Gmail API
   - Google Drive API
   - Google Calendar API
   - Google Sheets API
   - Google Docs API
   - Google Photos API
   - Google Contacts API
3. Create service account credentials
4. Download credentials JSON file
5. Place credentials in `config/credentials.json`

### 4. Configuration
```bash
cp config/config.example.json config/config.json
# Edit config.json with your settings
```

## 🔧 Configuration

### Environment Variables
```bash
export GOOGLE_APPLICATION_CREDENTIALS="path/to/credentials.json"
export MCP_SERVER_PORT=3000
export DEFAULT_SCHEDULE="0 2 * * *"  # Daily at 2 AM
export LOG_LEVEL="INFO"
```

### Configuration File (config/config.json)
```json
{
  "google_apis": {
    "credentials_path": "config/credentials.json",
    "enabled_services": [
      "gmail",
      "drive", 
      "calendar",
      "sheets",
      "docs",
      "photos",
      "contacts"
    ],
    "rate_limits": {
      "gmail": 1000,
      "drive": 1000,
      "calendar": 1000,
      "sheets": 100
    }
  },
  "services": {
    "gmail": {
      "backup_folder": "backups/gmail",
      "include_labels": ["INBOX", "SENT"],
      "exclude_labels": ["SPAM", "TRASH"]
    },
    "drive": {
      "backup_folder": "backups/drive",
      "include_folders": ["My Drive"],
      "exclude_folders": ["Trash"]
    },
    "calendar": {
      "backup_folder": "backups/calendar",
      "include_calendars": ["primary"],
      "date_range_days": 365
    }
  },
  "schedule": {
    "enabled": true,
    "default_cron": "0 2 * * *",
    "timezone": "UTC",
    "services": {
      "gmail": "0 2 * * *",
      "drive": "0 3 * * *",
      "calendar": "0 4 * * 0"
    }
  },
  "export": {
    "default_format": "json",
    "compression": true,
    "encryption": false,
    "formats": {
      "gmail": ["mbox", "json"],
      "drive": ["zip", "json"],
      "calendar": ["ics", "json"],
      "sheets": ["csv", "xlsx", "json"]
    }
  }
}
```

## 🚀 Usage

### Start the MCP Server
```bash
python -m mcp_google_services.server
```

### Service-Specific Operations

#### Gmail Operations
```bash
# Backup Gmail
python -m mcp_google_services.gmail --backup --user-id="user@example.com"

# Export emails
python -m mcp_google_services.gmail --export --format=mbox --date-range="2024-01-01:2024-12-31"
```

#### Google Drive Operations
```bash
# Backup Drive files
python -m mcp_google_services.drive --backup --folder-id="folder_id"

# Sync files
python -m mcp_google_services.drive --sync --local-path="./backups"
```

#### Google Calendar Operations
```bash
# Backup calendar events
python -m mcp_google_services.calendar --backup --calendar-id="primary"

# Export events
python -m mcp_google_services.calendar --export --format=ics --date-range="2024-01-01:2024-12-31"
```

#### Google Sheets Operations
```bash
# Backup spreadsheet
python -m mcp_google_services.sheets --backup --spreadsheet-id="spreadsheet_id"

# Export data
python -m mcp_google_services.sheets --export --format=csv --range="Sheet1!A1:Z100"
```

### Schedule Management
```bash
# Enable all services scheduling
python -m mcp_google_services.scheduler --enable-all

# Enable specific service scheduling
python -m mcp_google_services.scheduler --enable --service=gmail

# Check scheduling status
python -m mcp_google_services.scheduler --status
```

## 📊 API Endpoints

### MCP Tools by Service

#### Gmail Tools
- `gmail_backup`: Initiate Gmail backup
- `gmail_export`: Export Gmail data
- `gmail_search`: Search emails
- `gmail_labels`: Manage labels
- `gmail_status`: Check Gmail status

#### Google Drive Tools
- `drive_backup`: Backup Drive files
- `drive_sync`: Synchronize files
- `drive_search`: Search files
- `drive_permissions`: Manage permissions
- `drive_status`: Check Drive status

#### Google Calendar Tools
- `calendar_backup`: Backup calendar events
- `calendar_export`: Export events
- `calendar_create`: Create events
- `calendar_search`: Search events
- `calendar_status`: Check calendar status

#### Google Sheets Tools
- `sheets_backup`: Backup spreadsheet
- `sheets_export`: Export data
- `sheets_read`: Read cell data
- `sheets_write`: Write cell data
- `sheets_status`: Check sheets status

#### Multi-Service Tools
- `google_auth`: Manage authentication
- `google_quota`: Check API quotas
- `google_status`: Overall service status
- `google_schedule`: Manage scheduling
- `google_export`: Cross-service data export

### Example MCP Tool Usage
```json
{
  "tool": "gmail_backup",
  "arguments": {
    "user_id": "user@example.com",
    "labels": ["INBOX", "SENT"],
    "date_range": "2024-01-01:2024-12-31"
  }
}
```

```json
{
  "tool": "drive_backup",
  "arguments": {
    "folder_id": "folder_id",
    "recursive": true,
    "include_trash": false
  }
}
```

```json
{
  "tool": "google_export",
  "arguments": {
    "services": ["gmail", "drive", "calendar"],
    "format": "json",
    "compression": true
  }
}
```

## 📁 Project Structure

```
mcp-google-services/
├── src/
│   ├── mcp_google_services/
│   │   ├── server.py              # MCP server implementation
│   │   ├── core/
│   │   │   ├── auth.py            # Authentication management
│   │   │   ├── client.py          # Google API client base
│   │   │   └── scheduler.py       # Scheduling system
│   │   ├── services/
│   │   │   ├── gmail/
│   │   │   │   ├── api.py         # Gmail API client
│   │   │   │   ├── backup.py      # Gmail backup
│   │   │   │   └── export.py      # Gmail export
│   │   │   ├── drive/
│   │   │   │   ├── api.py         # Drive API client
│   │   │   │   ├── backup.py      # Drive backup
│   │   │   │   └── sync.py        # Drive sync
│   │   │   ├── calendar/
│   │   │   │   ├── api.py         # Calendar API client
│   │   │   │   ├── backup.py      # Calendar backup
│   │   │   │   └── export.py      # Calendar export
│   │   │   ├── sheets/
│   │   │   │   ├── api.py         # Sheets API client
│   │   │   │   ├── backup.py      # Sheets backup
│   │   │   │   └── operations.py  # Sheets operations
│   │   │   ├── docs/
│   │   │   │   ├── api.py         # Docs API client
│   │   │   │   └── operations.py  # Docs operations
│   │   │   ├── photos/
│   │   │   │   ├── api.py         # Photos API client
│   │   │   │   └── backup.py      # Photos backup
│   │   │   └── contacts/
│   │   │       ├── api.py         # Contacts API client
│   │   │       └── sync.py       # Contacts sync
│   │   └── utils/
│   │       ├── config.py          # Configuration management
│   │       ├── logging.py         # Logging utilities
│   │       ├── export.py          # Export utilities
│   │       └── rate_limiter.py    # Rate limiting
├── config/
│   ├── config.example.json        # Example configuration
│   └── credentials.json           # Google API credentials
├── tests/
│   ├── test_core/                # Core functionality tests
│   ├── test_services/            # Service-specific tests
│   └── test_integration/         # Integration tests
├── docs/
│   ├── api.md                    # API documentation
│   ├── setup.md                  # Setup guide
│   ├── services/                 # Service-specific docs
│   └── troubleshooting.md       # Troubleshooting guide
├── requirements.txt              # Python dependencies
├── pyproject.toml                # Project configuration
└── README.md                     # This file
```

## 🧪 Testing

### Run Tests
```bash
# Run all tests
pytest

# Run service-specific tests
pytest tests/test_services/test_gmail/
pytest tests/test_services/test_drive/

# Run with coverage
pytest --cov=mcp_google_services
```

### Test Configuration
```bash
# Use test credentials
export GOOGLE_APPLICATION_CREDENTIALS="config/test-credentials.json"
pytest tests/
```

## 📈 Monitoring

### Logs
```bash
# View server logs
tail -f logs/mcp-server.log

# View service-specific logs
tail -f logs/gmail.log
tail -f logs/drive.log
tail -f logs/calendar.log

# View scheduler logs
tail -f logs/scheduler.log
```

### Metrics
- Service-specific success rates
- API quota usage per service
- Processing time per operation
- Storage usage per service
- Authentication status

## 🔒 Security

### Data Protection
- **Encryption**: Optional encryption for backup files
- **Access Control**: Service account-based authentication
- **Audit Logging**: Comprehensive audit trail
- **Secure Storage**: Encrypted credential storage
- **Rate Limiting**: API quota protection

### Best Practices
- Use service accounts with minimal required permissions
- Regularly rotate API credentials
- Monitor API usage and quotas per service
- Implement proper error handling
- Use environment variables for sensitive data

## 🚨 Troubleshooting

### Common Issues

#### Authentication Errors
```bash
# Check credentials
python -c "from google.oauth2 import service_account; print('Credentials OK')"

# Verify API access
python -m mcp_google_services.core.auth --test
```

#### Service-Specific Issues
```bash
# Check Gmail API quota
python -m mcp_google_services.services.gmail.api --quota-status

# Check Drive API quota
python -m mcp_google_services.services.drive.api --quota-status

# Test service connectivity
python -m mcp_google_services.services.gmail.api --test
python -m mcp_google_services.services.drive.api --test
```

#### Scheduling Issues
```bash
# Check cron service
python -m mcp_google_services.core.scheduler --debug

# Verify timezone settings
python -c "import datetime; print(datetime.datetime.now())"
```

## 📚 Documentation

- [API Documentation](docs/api.md)
- [Setup Guide](docs/setup.md)
- [Service Documentation](docs/services/)
- [Troubleshooting](docs/troubleshooting.md)
- [Contributing Guidelines](CONTRIBUTING.md)
- [Security Policy](SECURITY.md)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run pre-commit hooks
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
