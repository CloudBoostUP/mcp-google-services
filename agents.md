# Agents Guide - Google Services MCP Server

This guide provides AI coding agents with the necessary context and instructions to effectively navigate and contribute to the Google Services MCP Server project.

## Project Overview

The Google Services MCP Server provides Model Context Protocol (MCP) integration for Google services, starting with Gmail. It enables automated backup, export, and management of Gmail data through MCP-compatible IDEs like Cursor.

## Project Structure

```
mcp-google-services/
├── src/                          # Source code
│   └── mcp_google_services/     # Main package
│       ├── core/                # Core functionality (auth, client, rate limiting)
│       ├── services/             # Service implementations (Gmail, etc.)
│       └── utils/               # Utility functions
├── docs/                        # Documentation
│   ├── AUTHENTICATION.md        # Authentication setup
│   ├── BACKUP_RESTORE_COMPLETE_GUIDE.md  # Complete backup/restore guide
│   ├── SCHEDULING_GUIDE.md      # Automated scheduling guide
│   └── STORAGE_MANAGEMENT.md    # Storage and retention guide
├── scripts/                     # Automation scripts
│   ├── backup_gmail.py         # Standalone backup script
│   └── cleanup_backups.py      # Backup cleanup script
├── config/                      # Configuration files
├── tests/                       # Test suite
└── README.md                    # Main documentation
```

## Pull Request Guidelines

### Public Repository Considerations

**CRITICAL**: This is a public repository. Never include internal or private information in PR descriptions or commit messages.

**Azure DevOps References:**
- ❌ **DO NOT** include Azure DevOps work item IDs, story numbers, or task references in PR descriptions
- ❌ **DO NOT** include Azure DevOps organization URLs or project names
- ❌ **DO NOT** include internal tracking information or sprint details
- ✅ **DO** use generic descriptions of features and changes
- ✅ **DO** focus on what the PR does, not internal tracking

**Example - WRONG:**
```
## Additional Context
- Azure DevOps Story: #1210
- All child tasks completed (#1351, #1352, #1353)
- Related to Sprint 3
```

**Example - RIGHT:**
```
## Additional Context
- Implements automated Gmail backup functionality
- Includes comprehensive documentation and testing
- Ready for production use
```

### PR Title Format

Use descriptive titles that explain what the PR does:
```
feat: Add automated Gmail backup scheduling
fix: Resolve MBOX file format validation issue
docs: Add comprehensive backup and restore guide
```

### PR Description Template

```markdown
## Description
Brief description of changes introduced by this PR.

## Purpose
What problem does this solve or what feature does this add?

## Overview
- List of key changes
- Features added
- Documentation updates

## Testing
How was this tested? What tests were run?

## Feedback Requested
Any specific areas you'd like reviewers to focus on?
```

## Code Style Guidelines

### Python Code
- **Style**: Follow PEP 8
- **Type Hints**: Use type hints for function parameters and return values
- **Docstrings**: Use Google-style docstrings
- **Error Handling**: Always use try-except blocks with meaningful error messages
- **Logging**: Use Python's logging module, not print statements

### Documentation
- **Format**: Markdown (.md files)
- **Structure**: Use clear headings (H1, H2, H3)
- **Code Blocks**: Use syntax highlighting
- **Links**: Use relative paths for internal links

## Testing Guidelines

### Running Tests
```bash
# Activate virtual environment
source .venv/bin/activate

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_services/test_gmail_integration.py -v

# Run with coverage
pytest tests/ --cov=mcp_google_services --cov-report=html
```

### Test Requirements
- All new features must include tests
- Tests should cover both success and error cases
- Integration tests should use test credentials, not production

## Security Guidelines

### Credentials Management
- **Never commit credentials**: OAuth credentials, API keys, or tokens
- **Use environment variables**: Store sensitive data in environment variables
- **Example files**: Use `.example` suffix for configuration templates
- **Git ignore**: Ensure `.gitignore` excludes all credential files

### Public Repository Safety
- **No internal URLs**: Don't include internal service URLs or endpoints
- **No organization names**: Don't reference specific client or organization names
- **No internal processes**: Don't document internal workflows or processes
- **Generic examples**: Use generic examples that don't reveal internal structure

## Documentation Standards

### When to Create Documentation
- **User-facing features**: Always document new features
- **API changes**: Document any API or interface changes
- **Setup procedures**: Document setup and configuration steps
- **Troubleshooting**: Document common issues and solutions

### Documentation Structure
- **Quick Start**: Provide a quick start guide for new users
- **Detailed Guides**: Create comprehensive guides for complex features
- **Examples**: Include practical examples in documentation
- **Cross-references**: Link related documentation sections

## Commit Message Guidelines

### Format
```
<type>: <subject>

<body>

<footer>
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Test additions or changes
- `chore`: Maintenance tasks

### Examples
```
feat: Add automated backup scheduling support

Implements cron-based scheduling for Gmail backups with
configurable retention policies.

docs: Update backup guide with retention examples

Adds examples for time-based and count-based retention policies.
```

## Common Tasks

### Adding a New Google Service
1. Create service module in `src/mcp_google_services/services/`
2. Implement API client following existing patterns
3. Add MCP tools in `server.py`
4. Create documentation in `docs/`
5. Add tests in `tests/test_services/`
6. Update README with new service

### Adding New MCP Tools
1. Implement tool function in appropriate service module
2. Register tool in `server.py` (both `list_tools()` and `call_tool()` handlers)
3. Add tool documentation
4. Create tests for the tool
5. Update usage examples

### Gmail Send Message Feature

**Status:** ✅ Implemented (November 2025)

**Implementation Details:**
- Added `send_message()` method to `GmailAPI` class (`src/mcp_google_services/services/gmail/api.py`)
- Added `gmail.send` scope to authentication (`src/mcp_google_services/core/auth.py`)
- Added `gmail_send_message` MCP tool to `server.py`
- Supports plain text and HTML emails
- Supports CC, BCC, and Reply-To headers

**Usage:**
```python
# Via MCP tool
{
  "tool": "gmail_send_message",
  "arguments": {
    "to": "recipient@example.com",
    "subject": "Test Email",
    "body": "Email body text",
    "cc": ["cc@example.com"],
    "bcc": ["bcc@example.com"]
  }
}
```

**Important Notes:**
- Requires `gmail.send` scope in OAuth credentials
- Quota cost: 100 units per email sent
- Email is sent immediately (no draft creation)
- Supports both plain text and HTML body formats

## Troubleshooting

### Common Issues
- **Authentication failures**: Check OAuth credentials and scopes
- **API quota exceeded**: Implement rate limiting (already included)
- **Import errors**: Ensure virtual environment is activated
- **MCP server not loading**: Check MCP configuration file format

## Resources

- **MCP Specification**: https://modelcontextprotocol.io/
- **Gmail API Documentation**: https://developers.google.com/gmail/api
- **Python Type Hints**: https://docs.python.org/3/library/typing.html
- **PEP 8 Style Guide**: https://pep8.org/

---

## Available MCP Tools

### Gmail Tools
- `gmail_backup` - Backup Gmail messages to MBOX format
- `gmail_export` - Export Gmail messages to various formats (MBOX, JSON, CSV, EML)
- `gmail_list_messages` - List Gmail messages with optional filtering
- `gmail_list_labels` - List all Gmail labels for a user
- `gmail_send_message` - Send email messages via Gmail API (NEW - November 2025)

---

**Last Updated**: November 2025  
**Maintained By**: CloudBoostUP Team

