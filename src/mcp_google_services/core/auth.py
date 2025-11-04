"""Authentication management for Google Services MCP Server."""

import os
import json
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.auth import default as google_auth_default
from google.auth.exceptions import DefaultCredentialsError, RefreshError
from google_auth_oauthlib.flow import InstalledAppFlow
import keyring

from ..utils.config import Config


class AuthManager:
    """Manages OAuth 2.0 authentication for Google APIs."""

    # Gmail API scopes
    GMAIL_SCOPES = [
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/gmail.metadata",
    ]

    def __init__(self, config: Optional[Config] = None):
        """Initialize AuthManager.

        Args:
            config: Optional configuration object. If None, loads from default paths.
        """
        self.config = config or Config()
        self.credentials_path = Path(self.config.get("google_apis.credentials_path", "config/credentials.json"))
        self.token_store_path = Path(self.config.get("auth.token_store", "config/tokens.json"))
        self.keyring_service = "mcp_google_services"
        
        # Ensure token directory exists
        self.token_store_path.parent.mkdir(parents=True, exist_ok=True)

    def get_credentials(self, user_id: str, scopes: Optional[List[str]] = None) -> Credentials:
        """Get authenticated credentials for a user.
        
        Authentication priority:
        1. Application Default Credentials (from `gcloud auth application-default login`)
        2. Stored OAuth credentials (from keyring/file)
        3. OAuth flow with credentials file (if exists)
        4. Prompt user to run `gcloud auth application-default login`

        Args:
            user_id: User email address or identifier
            scopes: Optional list of OAuth scopes. Defaults to Gmail scopes.

        Returns:
            Authenticated Credentials object

        Raises:
            FileNotFoundError: If credentials file doesn't exist and ADC not available
            RefreshError: If token refresh fails
        """
        scopes = scopes or self.GMAIL_SCOPES
        
        # Priority 1: Try Application Default Credentials (gcloud auth)
        try:
            # First try without scopes to get existing credentials
            credentials, project = google_auth_default()
            
            if credentials:
                # If credentials exist but don't have required scopes, we need to request them
                # For user credentials (not service accounts), we need to use OAuth flow for scopes
                if hasattr(credentials, 'requires_scopes') and credentials.requires_scopes(scopes):
                    # User credentials from gcloud auth don't support adding scopes directly
                    # We need to use OAuth flow to get credentials with proper scopes
                    # Check if credentials file exists for OAuth flow
                    if self.credentials_path.exists():
                        # Use OAuth flow with proper scopes
                        return self._authenticate_user(user_id, scopes)
                    else:
                        # No OAuth credentials file, raise error with instructions
                        raise FileNotFoundError(
                            f"Gmail API scopes are required but not present in current credentials.\n\n"
                            f"Please authenticate with Gmail scopes using one of these methods:\n\n"
                            f"Option 1 (OAuth 2.0 with credentials file):\n"
                            f"  1. Download OAuth 2.0 credentials from Google Cloud Console\n"
                            f"  2. Place them in: {self.credentials_path}\n"
                            f"  3. The MCP server will automatically request Gmail scopes\n\n"
                            f"Option 2 (Re-authenticate with gcloud):\n"
                            f"  Note: gcloud auth application-default login doesn't support Gmail scopes.\n"
                            f"  You'll need to use OAuth credentials file for Gmail API access.\n"
                        )
                
                # Credentials have required scopes, check if valid
                if credentials.expired:
                    credentials.refresh(Request())
                
                return credentials
        except DefaultCredentialsError:
            # ADC not available, continue to other methods
            pass
        except FileNotFoundError:
            # Re-raise FileNotFoundError (our custom error with instructions)
            raise
        except Exception as e:
            # Log but continue
            import logging
            logging.debug(f"ADC authentication failed: {e}")
        
        # Priority 2: Try to load existing stored credentials
        credentials = self._load_credentials(user_id)
        
        if credentials and credentials.valid:
            # Ensure scopes match
            if set(scopes).issubset(set(credentials.scopes or [])):
                return credentials
        
        # Try to refresh expired stored credentials
        if credentials and credentials.expired and credentials.refresh_token:
            try:
                credentials.refresh(Request())
                self._save_credentials(user_id, credentials)
                return credentials
            except RefreshError:
                # Refresh failed, need to re-authenticate
                pass
        
        # Priority 3: Try OAuth flow with credentials file (if exists)
        if self.credentials_path.exists():
            return self._authenticate_user(user_id, scopes)
        
        # Priority 4: Prompt user to run gcloud auth
        raise FileNotFoundError(
            f"No authentication credentials found.\n\n"
            "Please authenticate using one of these methods:\n\n"
            "Option 1 (Recommended - Similar to 'az login'):\n"
            "  Run: gcloud auth application-default login\n\n"
            "Option 2 (OAuth credentials file):\n"
            "  Download OAuth 2.0 credentials from Google Cloud Console\n"
            f"  and place them in: {self.credentials_path}\n\n"
            "After authentication, the MCP server will automatically use your credentials."
        )

    def _authenticate_user(self, user_id: str, scopes: List[str]) -> Credentials:
        """Perform OAuth 2.0 authentication flow.

        This will:
        1. Open your browser automatically
        2. Detect if you're already logged in to Google (reuses session!)
        3. Request Gmail permissions
        4. Store credentials securely for future use

        Args:
            user_id: User email address
            scopes: OAuth scopes to request

        Returns:
            Authenticated Credentials object
        """
        if not self.credentials_path.exists():
            raise FileNotFoundError(
                f"Credentials file not found: {self.credentials_path}\n"
                "Please download OAuth 2.0 credentials from Google Cloud Console "
                "and place them in the config directory.\n\n"
                "Quick setup:\n"
                "1. Go to https://console.cloud.google.com/apis/credentials\n"
                "2. Create OAuth client ID (Desktop app)\n"
                "3. Download JSON and save as config/credentials.json\n"
                "4. Enable Gmail API in APIs & Services > Library"
            )

        flow = InstalledAppFlow.from_client_secrets_file(
            str(self.credentials_path), scopes
        )
        
        # Run local server flow - this will:
        # - Open browser automatically
        # - Reuse existing Google login session if you're already logged in
        # - Only prompt for Gmail permissions
        credentials = flow.run_local_server(
            port=0,
            open_browser=True
        )
        
        # Save credentials for future use (stored securely, no need to re-authenticate)
        self._save_credentials(user_id, credentials)
        
        return credentials

    def _load_credentials(self, user_id: str) -> Optional[Credentials]:
        """Load stored credentials for a user.

        Args:
            user_id: User email address

        Returns:
            Credentials object if found, None otherwise
        """
        # Try loading from keyring first (most secure)
        token_data = self._load_from_keyring(user_id)
        
        if not token_data:
            # Fallback to file-based storage
            token_data = self._load_from_file(user_id)
        
        if not token_data:
            return None
        
        try:
            return Credentials.from_authorized_user_info(token_data)
        except Exception:
            return None

    def _save_credentials(self, user_id: str, credentials: Credentials) -> None:
        """Save credentials for a user.

        Args:
            user_id: User email address
            credentials: Credentials to save
        """
        token_data = {
            "token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "token_uri": credentials.token_uri,
            "client_id": credentials.client_id,
            "client_secret": credentials.client_secret,
            "scopes": credentials.scopes,
        }
        
        # Save to keyring (preferred)
        self._save_to_keyring(user_id, token_data)
        
        # Also save to file as backup
        self._save_to_file(user_id, token_data)

    def _load_from_keyring(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Load credentials from keyring.

        Args:
            user_id: User email address

        Returns:
            Token data dictionary or None
        """
        try:
            token_json = keyring.get_password(self.keyring_service, user_id)
            if token_json:
                return json.loads(token_json)
        except Exception:
            pass
        return None

    def _save_to_keyring(self, user_id: str, token_data: Dict[str, Any]) -> None:
        """Save credentials to keyring.

        Args:
            user_id: User email address
            token_data: Token data dictionary
        """
        try:
            token_json = json.dumps(token_data)
            keyring.set_password(self.keyring_service, user_id, token_json)
        except Exception:
            # Keyring may not be available on all platforms
            pass

    def _load_from_file(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Load credentials from file.

        Args:
            user_id: User email address

        Returns:
            Token data dictionary or None
        """
        if not self.token_store_path.exists():
            return None
        
        try:
            with open(self.token_store_path, "r") as f:
                all_tokens = json.load(f)
                return all_tokens.get(user_id)
        except Exception:
            return None

    def _save_to_file(self, user_id: str, token_data: Dict[str, Any]) -> None:
        """Save credentials to file.

        Args:
            user_id: User email address
            token_data: Token data dictionary
        """
        all_tokens = {}
        if self.token_store_path.exists():
            try:
                with open(self.token_store_path, "r") as f:
                    all_tokens = json.load(f)
            except Exception:
                pass
        
        all_tokens[user_id] = token_data
        
        with open(self.token_store_path, "w") as f:
            json.dump(all_tokens, f, indent=2)

    def revoke_credentials(self, user_id: str) -> None:
        """Revoke and remove credentials for a user.

        Args:
            user_id: User email address
        """
        credentials = self._load_credentials(user_id)
        
        if credentials:
            try:
                credentials.revoke(Request())
            except Exception:
                pass
        
        # Remove from keyring
        try:
            keyring.delete_password(self.keyring_service, user_id)
        except Exception:
            pass
        
        # Remove from file
        if self.token_store_path.exists():
            try:
                with open(self.token_store_path, "r") as f:
                    all_tokens = json.load(f)
                all_tokens.pop(user_id, None)
                with open(self.token_store_path, "w") as f:
                    json.dump(all_tokens, f, indent=2)
            except Exception:
                pass

