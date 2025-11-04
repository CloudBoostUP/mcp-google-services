"""Authentication management for Google Services MCP Server."""

import os
import json
from pathlib import Path
from typing import Optional, List, Dict, Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.exceptions import RefreshError
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

        Args:
            user_id: User email address or identifier
            scopes: Optional list of OAuth scopes. Defaults to Gmail scopes.

        Returns:
            Authenticated Credentials object

        Raises:
            FileNotFoundError: If credentials file doesn't exist
            RefreshError: If token refresh fails
        """
        scopes = scopes or self.GMAIL_SCOPES
        
        # Try to load existing credentials
        credentials = self._load_credentials(user_id)
        
        if credentials and credentials.valid:
            return credentials
        
        # Try to refresh expired credentials
        if credentials and credentials.expired and credentials.refresh_token:
            try:
                credentials.refresh(Request())
                self._save_credentials(user_id, credentials)
                return credentials
            except RefreshError:
                # Refresh failed, need to re-authenticate
                pass
        
        # Need to get new credentials
        return self._authenticate_user(user_id, scopes)

    def _authenticate_user(self, user_id: str, scopes: List[str]) -> Credentials:
        """Perform OAuth 2.0 authentication flow.

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
                "and place them in the config directory."
            )

        flow = InstalledAppFlow.from_client_secrets_file(
            str(self.credentials_path), scopes
        )
        
        # Run local server flow
        credentials = flow.run_local_server(port=0)
        
        # Save credentials for future use
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

