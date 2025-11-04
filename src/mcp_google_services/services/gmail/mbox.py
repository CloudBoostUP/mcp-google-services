"""MBOX format generation for email backup."""

import os
import time
from pathlib import Path
from typing import Dict, Any, Optional
from email.utils import formatdate, parsedate_to_datetime


class MBOXGenerator:
    """Generator for RFC 4155 compliant MBOX format files."""

    def __init__(self, output_path: str, encoding: str = "utf-8"):
        """Initialize MBOXGenerator.

        Args:
            output_path: Path to output MBOX file
            encoding: Character encoding (default: utf-8)
        """
        self.output_path = Path(output_path)
        self.encoding = encoding
        self.file = None
        self.message_count = 0
        
        # Ensure output directory exists
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

    def __enter__(self):
        """Context manager entry."""
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    def open(self) -> None:
        """Open MBOX file for writing."""
        if self.file is None:
            self.file = open(self.output_path, "ab")  # Append binary mode
            self.message_count = 0

    def close(self) -> None:
        """Close MBOX file."""
        if self.file:
            self.file.close()
            self.file = None

    def add_message(self, message: Dict[str, Any]) -> None:
        """Add a message to the MBOX file.

        Args:
            message: Parsed message dictionary (from EmailParser)
        """
        if self.file is None:
            self.open()

        # Generate "From " separator line (RFC 4155)
        from_line = self._format_from_line(message)
        self.file.write(from_line.encode(self.encoding))
        self.file.write(b"\n")

        # Write message content
        message_bytes = self._format_message(message)
        self.file.write(message_bytes)
        self.file.write(b"\n")  # Final newline

        self.message_count += 1

    def _format_from_line(self, message: Dict[str, Any]) -> str:
        """Generate RFC 4155 "From " separator line.

        Args:
            message: Parsed message dictionary

        Returns:
            "From " line string
        """
        # Get sender email address
        from_header = message.get("from", "")
        sender_email = self._extract_email(from_header) or "unknown@unknown"

        # Get date (use message date or current time)
        date = message.get("date")
        if date:
            # Format date as epoch time
            if isinstance(date, str):
                try:
                    date_obj = parsedate_to_datetime(date)
                    date_str = formatdate(time.mktime(date_obj.timetuple()))
                except Exception:
                    date_str = formatdate()
            else:
                # Assume it's a datetime object
                date_str = formatdate(time.mktime(date.timetuple()))
        else:
            date_str = formatdate()

        # Format: "From sender@example.com  Mon, 01 Jan 2024 12:00:00 +0000"
        return f"From {sender_email}  {date_str}"

    def _format_message(self, message: Dict[str, Any]) -> bytes:
        """Format message as RFC 822 bytes.

        Args:
            message: Parsed message dictionary

        Returns:
            RFC 822 formatted message bytes
        """
        from ..parser import EmailParser
        
        # Convert to RFC 822 format
        rfc822_bytes = EmailParser.to_rfc822(message)
        
        # Ensure message ends with newline
        if not rfc822_bytes.endswith(b"\n"):
            rfc822_bytes += b"\n"
        
        return rfc822_bytes

    def _extract_email(self, header_value: str) -> Optional[str]:
        """Extract email address from header value.

        Args:
            header_value: Header value (e.g., "Name <email@example.com>")

        Returns:
            Email address or None
        """
        if not header_value:
            return None

        # Try to extract email from common formats
        import re
        
        # Pattern: email@domain.com or <email@domain.com>
        email_pattern = r"[\w\.-]+@[\w\.-]+\.\w+"
        match = re.search(email_pattern, header_value)
        
        if match:
            return match.group(0)
        
        return None

    def get_message_count(self) -> int:
        """Get number of messages written.

        Returns:
            Message count
        """
        return self.message_count

    def get_file_size(self) -> int:
        """Get current file size.

        Returns:
            File size in bytes
        """
        if self.output_path.exists():
            return self.output_path.stat().st_size
        return 0

