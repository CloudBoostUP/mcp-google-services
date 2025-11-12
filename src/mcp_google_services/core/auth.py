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
    # Note: gmail.metadata doesn't support query parameters, so we use readonly for full access
    GMAIL_SCOPES = [
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/gmail.send",
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
        
        # Priority 1: If credentials.json exists, use OAuth flow (Gmail API requires OAuth scopes)
        # Gmail API doesn't work with Application Default Credentials (gcloud auth)
        # because ADC doesn't support Gmail scopes
        if self.credentials_path.exists():
            # Try to load existing stored OAuth credentials first
            credentials = self._load_credentials(user_id)
            
            if credentials and credentials.valid:
                # Check if credentials have required scopes
                existing_scopes = set(credentials.scopes or [])
                required_scopes = set(scopes)
                if required_scopes.issubset(existing_scopes):
                    return credentials
                else:
                    # Missing scopes, delete and re-authenticate
                    import logging
                    missing_scopes = required_scopes - existing_scopes
                    logging.info(f"Missing scopes: {missing_scopes}. Re-authenticating...")
                    self._delete_credentials(user_id)
            
            # Try to refresh expired credentials
            if credentials and credentials.expired and credentials.refresh_token:
                try:
                    credentials.refresh(Request())
                    existing_scopes = set(credentials.scopes or [])
                    required_scopes = set(scopes)
                    if required_scopes.issubset(existing_scopes):
                        self._save_credentials(user_id, credentials)
                        return credentials
                    else:
                        self._delete_credentials(user_id)
                except RefreshError:
                    pass
            
            # No valid credentials or missing scopes - start OAuth flow
            return self._authenticate_user(user_id, scopes)
        
        # Priority 2: Try Application Default Credentials (fallback for non-Gmail APIs)
        try:
            credentials, project = google_auth_default()
            if credentials:
                existing_scopes = set(getattr(credentials, 'scopes', []) or [])
                required_scopes = set(scopes)
                if required_scopes.issubset(existing_scopes):
                    if credentials.expired:
                        credentials.refresh(Request())
                    return credentials
                else:
                    raise FileNotFoundError(
                        f"Gmail API requires OAuth 2.0 credentials file.\n\n"
                        f"Please download OAuth 2.0 credentials from Google Cloud Console\n"
                        f"and place them in: {self.credentials_path}\n\n"
                        f"Note: gcloud auth application-default login doesn't support Gmail scopes.\n"
                    )
        except DefaultCredentialsError:
            pass
        except FileNotFoundError:
            raise
        except Exception as e:
            import logging
            logging.debug(f"ADC authentication failed: {e}")
        
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

    def _delete_credentials(self, user_id: str) -> None:
        """Delete stored credentials for a user (without revoking).

        Args:
            user_id: User email address
        """
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
                
                if user_id in all_tokens:
                    del all_tokens[user_id]
                    
                    if all_tokens:
                        with open(self.token_store_path, "w") as f:
                            json.dump(all_tokens, f, indent=2)
                    else:
                        # File is empty, delete it
                        self.token_store_path.unlink()
            except Exception:
                pass

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
        
        # Remove from storage
        self._delete_credentials(user_id)

