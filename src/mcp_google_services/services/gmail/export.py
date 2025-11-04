"""Gmail export operations in multiple formats."""

import json
import csv
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from .api import GmailAPI
from .parser import EmailParser
from .mbox import MBOXGenerator


class GmailExporter:
    """Gmail exporter supporting multiple formats."""

    SUPPORTED_FORMATS = ["mbox", "json", "eml", "csv"]

    def __init__(self, api: GmailAPI):
        """Initialize GmailExporter.

        Args:
            api: GmailAPI instance
        """
        self.api = api
        self.parser = EmailParser()

    def export_messages(
        self,
        user_id: str = "me",
        output_path: str = None,
        format: str = "mbox",
        query: Optional[str] = None,
        max_results: int = 1000,
        message_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Export messages in specified format.

        Args:
            user_id: User email address or 'me' (default: 'me')
            output_path: Path to output file (optional, auto-generated if not provided)
            format: Export format ('mbox', 'json', 'eml', 'csv')
            query: Optional Gmail query string
            max_results: Maximum number of messages
            message_ids: Optional list of specific message IDs to export

        Returns:
            Dictionary with export results

        Raises:
            ValueError: If format is not supported
        """
        if format not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported format: {format}. Supported: {self.SUPPORTED_FORMATS}")

        # Generate output path if not provided
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_folder = Path("exports/gmail")
            export_folder.mkdir(parents=True, exist_ok=True)
            output_path = export_folder / f"gmail_export_{timestamp}.{format}"

        output_path = Path(output_path)

        # Get messages
        if message_ids:
            messages = self.api.batch_get_messages(
                user_id=user_id,
                message_ids=message_ids,
                format="full",
            )
        else:
            # List messages
            all_message_ids = []
            page_token = None
            
            while len(all_message_ids) < max_results:
                list_result = self.api.list_messages(
                    user_id=user_id,
                    query=query,
                    max_results=min(100, max_results - len(all_message_ids)),
                    page_token=page_token,
                )
                
                messages = list_result.get("messages", [])
                if not messages:
                    break
                
                all_message_ids.extend([msg["id"] for msg in messages])
                page_token = list_result.get("nextPageToken")
                
                if not page_token:
                    break
            
            # Get full messages
            all_message_ids = all_message_ids[:max_results]
            if all_message_ids:
                messages = self.api.batch_get_messages(
                    user_id=user_id,
                    message_ids=all_message_ids,
                    format="full",
                )
            else:
                messages = []

        # Export based on format
        if format == "mbox":
            return self._export_to_mbox(messages, output_path)
        elif format == "json":
            return self._export_to_json(messages, output_path)
        elif format == "eml":
            return self._export_to_eml(messages, output_path)
        elif format == "csv":
            return self._export_to_csv(messages, output_path)

    def _export_to_mbox(self, messages: List[Dict[str, Any]], output_path: Path) -> Dict[str, Any]:
        """Export messages to MBOX format.

        Args:
            messages: List of Gmail API message objects
            output_path: Path to output MBOX file

        Returns:
            Export result dictionary
        """
        message_count = 0
        
        with MBOXGenerator(str(output_path)) as mbox:
            for message in messages:
                try:
                    parsed = self.parser.parse_message(message)
                    mbox.add_message(parsed)
                    message_count += 1
                except Exception:
                    # Skip messages that fail to parse
                    continue
        
        return {
            "format": "mbox",
            "output_path": str(output_path),
            "message_count": message_count,
            "file_size": output_path.stat().st_size if output_path.exists() else 0,
        }

    def _export_to_json(self, messages: List[Dict[str, Any]], output_path: Path) -> Dict[str, Any]:
        """Export messages to JSON format.

        Args:
            messages: List of Gmail API message objects
            output_path: Path to output JSON file

        Returns:
            Export result dictionary
        """
        parsed_messages = []
        
        for message in messages:
            try:
                parsed = self.parser.parse_message(message)
                parsed_messages.append(parsed)
            except Exception:
                # Skip messages that fail to parse
                continue
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(parsed_messages, f, indent=2, default=str)
        
        return {
            "format": "json",
            "output_path": str(output_path),
            "message_count": len(parsed_messages),
            "file_size": output_path.stat().st_size if output_path.exists() else 0,
        }

    def _export_to_eml(self, messages: List[Dict[str, Any]], output_path: Path) -> Dict[str, Any]:
        """Export messages to individual EML files.

        Args:
            messages: List of Gmail API message objects
            output_path: Path to output directory (will create EML files inside)

        Returns:
            Export result dictionary
        """
        # Create output directory if it doesn't exist
        if output_path.suffix:
            # If it's a file path, use parent directory
            output_dir = output_path.parent / output_path.stem
        else:
            output_dir = output_path
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        message_count = 0
        
        for message in messages:
            try:
                parsed = self.parser.parse_message(message)
                
                # Generate filename from message ID
                message_id = parsed.get("id", f"message_{message_count}")
                eml_path = output_dir / f"{message_id}.eml"
                
                # Write RFC 822 format
                rfc822_bytes = self.parser.to_rfc822(parsed)
                with open(eml_path, "wb") as f:
                    f.write(rfc822_bytes)
                
                message_count += 1
            except Exception:
                # Skip messages that fail to parse
                continue
        
        return {
            "format": "eml",
            "output_path": str(output_dir),
            "message_count": message_count,
            "file_count": message_count,
        }

    def _export_to_csv(self, messages: List[Dict[str, Any]], output_path: Path) -> Dict[str, Any]:
        """Export messages to CSV format.

        Args:
            messages: List of Gmail API message objects
            output_path: Path to output CSV file

        Returns:
            Export result dictionary
        """
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        rows = []
        
        for message in messages:
            try:
                parsed = self.parser.parse_message(message)
                
                row = {
                    "id": parsed.get("id", ""),
                    "thread_id": parsed.get("thread_id", ""),
                    "date": parsed.get("date", ""),
                    "from": parsed.get("from", ""),
                    "to": parsed.get("to", ""),
                    "subject": parsed.get("subject", ""),
                    "snippet": parsed.get("snippet", ""),
                    "label_ids": ",".join(parsed.get("label_ids", [])),
                    "size_estimate": parsed.get("size_estimate", 0),
                    "has_attachments": len(parsed.get("attachments", [])) > 0,
                    "attachment_count": len(parsed.get("attachments", [])),
                }
                rows.append(row)
            except Exception:
                # Skip messages that fail to parse
                continue
        
        # Write CSV
        if rows:
            fieldnames = rows[0].keys()
            with open(output_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
        
        return {
            "format": "csv",
            "output_path": str(output_path),
            "message_count": len(rows),
            "file_size": output_path.stat().st_size if output_path.exists() else 0,
        }

