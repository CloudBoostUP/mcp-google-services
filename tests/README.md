# Testing Guide for Gmail MCP Server

This directory contains comprehensive tests for the Gmail MCP server implementation.

## Test Structure

```
tests/
├── test_core/              # Core functionality tests
├── test_services/          # Service-specific tests
│   └── test_gmail_integration.py
├── test_integration/      # End-to-end integration tests
│   └── test_gmail_end_to_end.py
└── README.md              # This file
```

## Test Files

### 1. `test_gmail_integration.py`
Comprehensive pytest-based integration tests covering:
- Authentication (OAuth 2.0 flow)
- Gmail API operations (list, get, batch get, labels)
- Email parsing
- MBOX generation
- Backup operations
- Export operations (MBOX, JSON, CSV, EML)
- Rate limiting

### 2. `test_gmail_end_to_end.py`
Complete end-to-end workflow test that verifies:
- Configuration loading
- Authentication
- Gmail API integration
- Backup operations
- Export operations

### 3. `test_gmail_server.py` (root directory)
Interactive manual test script for ad-hoc testing without pytest.

## Running Tests

### Prerequisites

1. **OAuth Credentials**: 
   - Download OAuth 2.0 credentials from Google Cloud Console
   - Place in `config/credentials.json`
   - Ensure Gmail API is enabled in your Google Cloud Project

2. **Environment Setup**:
   ```bash
   # Activate virtual environment
   source .venv/bin/activate
   
   # Install test dependencies (if not already installed)
   pip install -r requirements-dev.txt
   ```

### Running Pytest Tests

```bash
# Run all integration tests
pytest tests/test_services/test_gmail_integration.py -v -m integration

# Run specific test class
pytest tests/test_services/test_gmail_integration.py::TestGmailAPI -v

# Run specific test
pytest tests/test_services/test_gmail_integration.py::TestGmailAPI::test_list_messages -v

# Run with coverage
pytest tests/test_services/test_gmail_integration.py --cov=mcp_google_services --cov-report=html
```

### Running End-to-End Test

```bash
# Run end-to-end test
python tests/test_integration/test_gmail_end_to_end.py
```

### Running Manual Test Script

```bash
# Run interactive test script
python test_gmail_server.py

# Or set user email
TEST_GMAIL_USER=your.email@gmail.com python test_gmail_server.py
```

## Test Markers

Tests are marked with `@pytest.mark.integration` for integration tests that require:
- Actual Gmail account
- OAuth credentials
- Network access

To skip integration tests:
```bash
pytest -m "not integration"
```

## Expected Test Results

### Successful Test Run

When all tests pass, you should see:
- ✓ Authentication successful
- ✓ Gmail API operations working
- ✓ Backup operations completing
- ✓ Export operations generating files
- ✓ All test files cleaned up

### Common Issues

1. **Credentials Not Found**:
   - Ensure `config/credentials.json` exists
   - Verify OAuth credentials are properly configured

2. **Authentication Failed**:
   - Check OAuth consent screen settings
   - Verify Gmail API is enabled in Google Cloud Console
   - Ensure scopes are correct

3. **Rate Limiting**:
   - Gmail API has quotas (250 units/second)
   - Tests may need to wait between requests
   - Reduce `max_results` if hitting limits

4. **No Messages Found**:
   - Ensure test Gmail account has some emails
   - Adjust query filters if needed

## Test Coverage

The test suite covers:

- ✅ Authentication flow (OAuth 2.0)
- ✅ Gmail API client operations
- ✅ Rate limiting functionality
- ✅ Email parsing and processing
- ✅ MBOX format generation
- ✅ Incremental and full backup
- ✅ Multiple export formats (MBOX, JSON, CSV, EML)
- ✅ Error handling and recovery
- ✅ State management

## Continuous Integration

For CI/CD pipelines:

1. Set up OAuth credentials as secrets
2. Use test Gmail account credentials
3. Mark integration tests appropriately
4. Run unit tests (without integration marker) in CI
5. Run integration tests manually or in scheduled jobs

## Troubleshooting

### Test Failures

1. **Check credentials**: Verify OAuth credentials are valid
2. **Check API quotas**: Ensure not hitting Gmail API limits
3. **Check network**: Verify internet connectivity
4. **Check permissions**: Ensure Gmail API scopes are granted

### Debug Mode

Run tests with verbose output:
```bash
pytest -v -s tests/test_services/test_gmail_integration.py
```

The `-s` flag shows print statements for debugging.

