"""Email parsing and processing utilities."""

import base64
import email
from email.header import decode_header
from typing import Dict, Any, List, Optional
from datetime import datetime


class EmailParser:
    """Parser for Gmail API message objects."""

    @staticmethod
    def parse_message(message: Dict[str, Any]) -> Dict[str, Any]:
        """Parse a Gmail API message into a structured format.

        Args:
            message: Gmail API message object

        Returns:
            Parsed message dictionary with headers, body, attachments, etc.
        """
        parsed = {
            "id": message.get("id"),
            "thread_id": message.get("threadId"),
            "label_ids": message.get("labelIds", []),
            "snippet": message.get("snippet", ""),
            "size_estimate": message.get("sizeEstimate", 0),
            "headers": {},
            "body": {},
            "attachments": [],
            "date": None,
            "from": None,
            "to": None,
            "subject": None,
        }

        # Parse headers
        payload = message.get("payload", {})
        headers = payload.get("headers", [])
        
        for header in headers:
            name = header.get("name", "").lower()
            value = header.get("value", "")
            parsed["headers"][name] = value

        # Extract common headers
        parsed["from"] = parsed["headers"].get("from", "")
        parsed["to"] = parsed["headers"].get("to", "")
        parsed["subject"] = EmailParser._decode_header(parsed["headers"].get("subject", ""))
        date_str = parsed["headers"].get("date", "")
        parsed["date"] = EmailParser._parse_date(date_str)

        # Parse body and attachments
        parsed["body"], parsed["attachments"] = EmailParser._parse_payload(
            payload, message.get("raw")
        )

        return parsed

    @staticmethod
    def _parse_payload(
        payload: Dict[str, Any],
        raw_message: Optional[str] = None
    ) -> tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """Parse message payload (body and attachments).

        Args:
            payload: Gmail API payload object
            raw_message: Optional raw RFC 822 message string

        Returns:
            Tuple of (body_dict, attachments_list)
        """
        body = {"text": "", "html": ""}
        attachments = []

        if raw_message:
            # Parse raw message if available
            raw_decoded = base64.urlsafe_b64decode(raw_message)
            email_message = email.message_from_bytes(raw_decoded)
            
            body["text"], body["html"] = EmailParser._extract_body_from_email(
                email_message
            )
            attachments = EmailParser._extract_attachments_from_email(email_message)
        else:
            # Parse from payload structure
            body, attachments = EmailParser._parse_payload_structure(payload)

        return body, attachments

    @staticmethod
    def _parse_payload_structure(
        payload: Dict[str, Any]
    ) -> tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """Parse payload structure from Gmail API.

        Args:
            payload: Gmail API payload object

        Returns:
            Tuple of (body_dict, attachments_list)
        """
        body = {"text": "", "html": ""}
        attachments = []

        mime_type = payload.get("mimeType", "")
        parts = payload.get("parts", [])

        # Single part message
        if not parts:
            body_data = payload.get("body", {})
            data = body_data.get("data", "")
            
            if data:
                decoded = EmailParser._decode_body_data(data)
                if "text/plain" in mime_type:
                    body["text"] = decoded
                elif "text/html" in mime_type:
                    body["html"] = decoded
                else:
                    # Treat as text if unknown
                    body["text"] = decoded

        # Multipart message
        else:
            for part in parts:
                part_mime_type = part.get("mimeType", "")
                part_body = part.get("body", {})
                part_data = part_body.get("data", "")
                filename = part_body.get("filename", "")
                attachment_id = part_body.get("attachmentId")

                if attachment_id or filename:
                    # This is an attachment
                    attachments.append({
                        "attachment_id": attachment_id,
                        "filename": filename,
                        "mime_type": part_mime_type,
                        "size": part_body.get("size", 0),
                    })
                elif part_data:
                    # This is a body part
                    decoded = EmailParser._decode_body_data(part_data)
                    if "text/plain" in part_mime_type:
                        body["text"] = decoded
                    elif "text/html" in part_mime_type:
                        body["html"] = decoded

        return body, attachments

    @staticmethod
    def _extract_body_from_email(email_message: email.message.Message) -> tuple[str, str]:
        """Extract text and HTML body from email.message object.

        Args:
            email_message: email.message.Message object

        Returns:
            Tuple of (text_body, html_body)
        """
        text_body = ""
        html_body = ""

        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition", ""))

                # Skip attachments
                if "attachment" in content_disposition:
                    continue

                payload = part.get_payload(decode=True)
                if payload:
                    try:
                        decoded = payload.decode("utf-8", errors="ignore")
                        if content_type == "text/plain":
                            text_body = decoded
                        elif content_type == "text/html":
                            html_body = decoded
                    except Exception:
                        pass
        else:
            # Single part message
            payload = email_message.get_payload(decode=True)
            if payload:
                try:
                    decoded = payload.decode("utf-8", errors="ignore")
                    content_type = email_message.get_content_type()
                    if "text/plain" in content_type:
                        text_body = decoded
                    elif "text/html" in content_type:
                        html_body = decoded
                    else:
                        text_body = decoded
                except Exception:
                    pass

        return text_body, html_body

    @staticmethod
    def _extract_attachments_from_email(
        email_message: email.message.Message
    ) -> List[Dict[str, Any]]:
        """Extract attachment information from email.message object.

        Args:
            email_message: email.message.Message object

        Returns:
            List of attachment dictionaries
        """
        attachments = []

        if email_message.is_multipart():
            for part in email_message.walk():
                content_disposition = str(part.get("Content-Disposition", ""))

                if "attachment" in content_disposition:
                    filename = part.get_filename()
                    if filename:
                        filename = EmailParser._decode_header(filename)
                        attachments.append({
                            "filename": filename,
                            "mime_type": part.get_content_type(),
                            "size": len(part.get_payload(decode=True) or b""),
                        })

        return attachments

    @staticmethod
    def _decode_header(header_value: str) -> str:
        """Decode email header value (handles encoded words).

        Args:
            header_value: Header value that may be encoded

        Returns:
            Decoded header value
        """
        if not header_value:
            return ""

        try:
            decoded_parts = decode_header(header_value)
            decoded_string = ""
            for part, encoding in decoded_parts:
                if isinstance(part, bytes):
                    decoded_string += part.decode(encoding or "utf-8", errors="ignore")
                else:
                    decoded_string += part
            return decoded_string
        except Exception:
            return header_value

    @staticmethod
    def _decode_body_data(data: str) -> str:
        """Decode base64url-encoded body data.

        Args:
            data: Base64url-encoded string

        Returns:
            Decoded string
        """
        try:
            # Gmail API uses base64url encoding
            # Add padding if needed
            missing_padding = len(data) % 4
            if missing_padding:
                data += "=" * (4 - missing_padding)
            
            decoded_bytes = base64.urlsafe_b64decode(data)
            return decoded_bytes.decode("utf-8", errors="ignore")
        except Exception:
            return ""

    @staticmethod
    def _parse_date(date_str: str) -> Optional[datetime]:
        """Parse email date string to datetime.

        Args:
            date_str: Date string from email header

        Returns:
            datetime object or None if parsing fails
        """
        if not date_str:
            return None

        try:
            # Try parsing with email.utils
            timestamp = email.utils.parsedate_to_datetime(date_str)
            return timestamp
        except Exception:
            try:
                # Fallback to datetime parsing
                from dateutil import parser
                return parser.parse(date_str)
            except Exception:
                return None

    @staticmethod
    def to_rfc822(message: Dict[str, Any]) -> bytes:
        """Convert parsed message back to RFC 822 format.

        Args:
            message: Parsed message dictionary

        Returns:
            RFC 822 formatted email as bytes
        """
        email_message = email.message.EmailMessage()

        # Set headers
        for name, value in message.get("headers", {}).items():
            email_message[name] = value

        # Set body
        body = message.get("body", {})
        if body.get("html"):
            email_message.set_content(body["html"], subtype="html")
            if body.get("text"):
                # Add text as alternative
                text_part = email.message.EmailMessage()
                text_part.set_content(body["text"], subtype="plain")
                email_message.make_alternative()
                email_message.attach(text_part)
        elif body.get("text"):
            email_message.set_content(body["text"], subtype="plain")

        return email_message.as_bytes()

