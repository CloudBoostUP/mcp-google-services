#!/usr/bin/env python3
"""Quick test to verify OAuth credentials work."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from mcp_google_services.utils.config import Config
from mcp_google_services.core.auth import AuthManager

print("🔐 Testing OAuth credentials...")
print()

config = Config()
auth_manager = AuthManager(config=config)

try:
    print("Attempting to authenticate with OAuth credentials...")
    credentials = auth_manager.get_credentials("me")
    print("✅ Authentication successful!")
    print(f"   Token valid: {credentials.valid}")
    print(f"   Has refresh token: {credentials.refresh_token is not None}")
    print(f"   Scopes: {', '.join(credentials.scopes) if credentials.scopes else 'None'}")
    print()
    print("🎉 Ready to use Gmail API!")
except Exception as e:
    print(f"❌ Authentication failed: {e}")
    import traceback
    traceback.print_exc()

