"""Gmail backup operations."""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict

from .api import GmailAPI
from .parser import EmailParser
from .mbox import MBOXGenerator
from ...utils.config import Config


@dataclass
class BackupResult:
    """Result of a backup operation."""

    success: bool
    message_count: int
    backup_path: str
    start_time: datetime
    end_time: Optional[datetime] = None
    error: Optional[str] = None
    messages_processed: int = 0
    messages_failed: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = asdict(self)
        result["start_time"] = self.start_time.isoformat()
        if self.end_time:
            result["end_time"] = self.end_time.isoformat()
        return result


class GmailBackup:
    """Gmail backup service."""

    def __init__(self, api: GmailAPI, config: Optional[Config] = None):
        """Initialize GmailBackup.

        Args:
            api: GmailAPI instance
            config: Optional configuration object
        """
        self.api = api
        self.config = config or Config()
        self.backup_folder = Path(self.config.get("gmail.backup_folder", "backups/gmail"))
        self.state_file = self.backup_folder / "backup_state.json"
        self.parser = EmailParser()
        
        # Ensure backup folder exists
        self.backup_folder.mkdir(parents=True, exist_ok=True)

    def incremental_backup(
        self,
        user_id: str = "me",
        query: Optional[str] = None,
        max_results: Optional[int] = None,
    ) -> BackupResult:
        """Perform incremental backup (only new messages since last backup).

        Args:
            user_id: User email address or 'me' (default: 'me')
            query: Optional Gmail query string
            max_results: Maximum number of messages (default: from config)

        Returns:
            BackupResult object
        """
        start_time = datetime.now()
        
        try:
            # Load last backup state
            last_backup_time = self._get_last_backup_time(user_id)
            
            # Build query for new messages
            if not query:
                if last_backup_time:
                    # Only get messages after last backup
                    query = f"after:{int(last_backup_time.timestamp())}"
                else:
                    # First backup - get all messages
                    query = None
            
            # Get backup configuration
            if max_results is None:
                max_results = self.config.get("gmail.max_messages_per_backup", 1000)
            
            # Perform backup
            result = self._backup_messages(
                user_id=user_id,
                query=query,
                max_results=max_results,
                backup_type="incremental",
            )
            
            # Update backup state
            if result.success:
                self._update_backup_state(user_id, start_time)
            
            result.start_time = start_time
            result.end_time = datetime.now()
            
            return result
            
        except Exception as e:
            return BackupResult(
                success=False,
                message_count=0,
                backup_path="",
                start_time=start_time,
                end_time=datetime.now(),
                error=str(e),
            )

    def full_backup(
        self,
        user_id: str = "me",
        query: Optional[str] = None,
        max_results: Optional[int] = None,
    ) -> BackupResult:
        """Perform full backup of all messages.

        Args:
            user_id: User email address or 'me' (default: 'me')
            query: Optional Gmail query string
            max_results: Maximum number of messages (default: from config)

        Returns:
            BackupResult object
        """
        start_time = datetime.now()
        
        try:
            if max_results is None:
                max_results = self.config.get("gmail.max_messages_per_backup", 10000)
            
            result = self._backup_messages(
                user_id=user_id,
                query=query,
                max_results=max_results,
                backup_type="full",
            )
            
            result.start_time = start_time
            result.end_time = datetime.now()
            
            return result
            
        except Exception as e:
            return BackupResult(
                success=False,
                message_count=0,
                backup_path="",
                start_time=start_time,
                end_time=datetime.now(),
                error=str(e),
            )

    def _backup_messages(
        self,
        user_id: str,
        query: Optional[str] = None,
        max_results: int = 1000,
        backup_type: str = "incremental",
    ) -> BackupResult:
        """Internal method to backup messages.

        Args:
            user_id: User email address
            query: Gmail query string
            max_results: Maximum number of messages
            backup_type: Type of backup ('incremental' or 'full')

        Returns:
            BackupResult object
        """
        # Generate backup filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"gmail_backup_{backup_type}_{timestamp}.mbox"
        backup_path = self.backup_folder / backup_filename
        
        message_ids = []
        page_token = None
        
        # Collect all message IDs
        while len(message_ids) < max_results:
            list_result = self.api.list_messages(
                user_id=user_id,
                query=query,
                max_results=min(100, max_results - len(message_ids)),
                page_token=page_token,
            )
            
            messages = list_result.get("messages", [])
            if not messages:
                break
            
            message_ids.extend([msg["id"] for msg in messages])
            page_token = list_result.get("nextPageToken")
            
            if not page_token:
                break
        
        # Limit to max_results
        message_ids = message_ids[:max_results]
        
        if not message_ids:
            return BackupResult(
                success=True,
                message_count=0,
                backup_path=str(backup_path),
                start_time=datetime.now(),
            )
        
        # Process messages in batches
        messages_processed = 0
        messages_failed = 0
        
        with MBOXGenerator(str(backup_path)) as mbox:
            batch_size = 100
            
            for i in range(0, len(message_ids), batch_size):
                batch = message_ids[i:i + batch_size]
                
                # Get messages in batch
                try:
                    messages = self.api.batch_get_messages(
                        user_id=user_id,
                        message_ids=batch,
                        format="full",
                    )
                    
                    # Parse and add to MBOX
                    for message in messages:
                        try:
                            parsed = self.parser.parse_message(message)
                            mbox.add_message(parsed)
                            messages_processed += 1
                        except Exception as e:
                            messages_failed += 1
                            # Continue with next message
                            continue
                            
                except Exception as e:
                    messages_failed += len(batch)
                    # Continue with next batch
                    continue
        
        return BackupResult(
            success=True,
            message_count=messages_processed,
            backup_path=str(backup_path),
            start_time=datetime.now(),
            messages_processed=messages_processed,
            messages_failed=messages_failed,
        )

    def _get_last_backup_time(self, user_id: str) -> Optional[datetime]:
        """Get timestamp of last backup for user.

        Args:
            user_id: User email address

        Returns:
            datetime of last backup or None
        """
        if not self.state_file.exists():
            return None
        
        try:
            with open(self.state_file, "r") as f:
                state = json.load(f)
                user_state = state.get(user_id, {})
                last_backup_str = user_state.get("last_backup_time")
                if last_backup_str:
                    return datetime.fromisoformat(last_backup_str)
        except Exception:
            pass
        
        return None

    def _update_backup_state(self, user_id: str, backup_time: datetime) -> None:
        """Update backup state file.

        Args:
            user_id: User email address
            backup_time: Time of backup
        """
        state = {}
        if self.state_file.exists():
            try:
                with open(self.state_file, "r") as f:
                    state = json.load(f)
            except Exception:
                pass
        
        if user_id not in state:
            state[user_id] = {}
        
        state[user_id]["last_backup_time"] = backup_time.isoformat()
        state[user_id]["last_backup_type"] = "incremental"
        
        with open(self.state_file, "w") as f:
            json.dump(state, f, indent=2)

