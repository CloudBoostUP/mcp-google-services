"""MCP Server entry point for Google Services.

This module provides the main entry point for the Model Context Protocol (MCP) server
that enables Gmail backup and Google services management.
"""

import sys
import asyncio
from pathlib import Path
from typing import Any

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from mcp_google_services.utils.config import Config
from mcp_google_services.core.auth import AuthManager
from mcp_google_services.services.gmail.api import GmailAPI
from mcp_google_services.services.gmail.backup import GmailBackup
from mcp_google_services.services.gmail.export import GmailExporter


# Create MCP server instance
app = Server("google-services")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools."""
    return [
        Tool(
            name="gmail_backup",
            description="Backup Gmail messages to MBOX format. Supports incremental and full backups.",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "Gmail user ID (default: 'me')",
                        "default": "me"
                    },
                    "backup_type": {
                        "type": "string",
                        "enum": ["incremental", "full"],
                        "description": "Type of backup to perform",
                        "default": "incremental"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of messages to backup",
                        "default": 1000
                    },
                    "query": {
                        "type": "string",
                        "description": "Optional Gmail query string to filter messages"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="gmail_export",
            description="Export Gmail messages to various formats (MBOX, JSON, CSV, EML).",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "Gmail user ID (default: 'me')",
                        "default": "me"
                    },
                    "format": {
                        "type": "string",
                        "enum": ["mbox", "json", "csv", "eml"],
                        "description": "Export format",
                        "default": "mbox"
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Output file path (optional, auto-generated if not provided)"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of messages to export",
                        "default": 100
                    },
                    "query": {
                        "type": "string",
                        "description": "Optional Gmail query string to filter messages"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="gmail_list_messages",
            description="List Gmail messages with optional filtering.",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "Gmail user ID (default: 'me')",
                        "default": "me"
                    },
                    "query": {
                        "type": "string",
                        "description": "Gmail search query (e.g., 'from:example@gmail.com', 'has:attachment')"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of messages to return",
                        "default": 10
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="gmail_list_labels",
            description="List all Gmail labels for a user.",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "Gmail user ID (default: 'me')",
                        "default": "me"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="gmail_send_message",
            description="Send an email message via Gmail.",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "Gmail user ID (default: 'me')",
                        "default": "me"
                    },
                    "to": {
                        "type": "string",
                        "description": "Recipient email address (required)"
                    },
                    "subject": {
                        "type": "string",
                        "description": "Email subject (required)"
                    },
                    "body": {
                        "type": "string",
                        "description": "Plain text email body (required if body_html not provided)"
                    },
                    "body_html": {
                        "type": "string",
                        "description": "HTML email body (optional, if provided will be used instead of body)"
                    },
                    "cc": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of CC email addresses (optional)"
                    },
                    "bcc": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of BCC email addresses (optional)"
                    },
                    "reply_to": {
                        "type": "string",
                        "description": "Reply-To email address (optional)"
                    }
                },
                "required": ["to", "subject"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls."""
    try:
        config = Config()
        auth_manager = AuthManager(config=config)
        
        user_id = arguments.get("user_id", "me")
        
        # Authenticate
        try:
            # Run authentication in thread pool to avoid blocking async context
            # OAuth flow may open browser and block, so run it in separate thread
            credentials = await asyncio.to_thread(auth_manager.get_credentials, user_id)
        except FileNotFoundError as e:
            error_msg = str(e)
            # Check if credentials.json exists - if so, OAuth flow should work
            from pathlib import Path
            credentials_path = Path(auth_manager.config.get("google_apis.credentials_path", "config/credentials.json"))
            
            if credentials_path.exists():
                # Credentials file exists, OAuth flow should work
                # This error shouldn't happen, but if it does, provide OAuth instructions
                return [
                    TextContent(
                        type="text",
                        text=f"🔐 OAuth Authentication Required\n\n"
                             f"Credentials file found, but authentication failed.\n\n"
                             f"This may happen if:\n"
                             f"  • OAuth consent screen needs new scopes added\n"
                             f"  • You need to be added as a test user\n"
                             f"  • Token storage needs to be cleared\n\n"
                             f"Try running the setup script:\n"
                             f"  python setup_oauth.py\n\n"
                             f"Or manually delete tokens and try again:\n"
                             f"  rm config/tokens.json\n\n"
                             f"Error details: {error_msg}"
                    )
                ]
            else:
                # No credentials file - provide setup instructions
                if "gcloud auth application-default login" in error_msg:
                    return [
                        TextContent(
                            type="text",
                            text=f"🔐 Authentication Required\n\n"
                                 f"For Gmail API, you need OAuth 2.0 credentials file:\n\n"
                                 f"  1. Download OAuth 2.0 credentials from Google Cloud Console\n"
                                 f"  2. Place them in: {credentials_path}\n"
                                 f"  3. Run: python setup_oauth.py\n\n"
                                 f"Note: gcloud auth application-default login doesn't support Gmail scopes.\n"
                        )
                    ]
                else:
                    return [
                        TextContent(
                            type="text",
                            text=f"Error: {error_msg}"
                        )
                    ]
        except Exception as e:
            return [
                TextContent(
                    type="text",
                    text=f"Authentication error: {str(e)}"
                )
            ]
        
        if name == "gmail_backup":
            backup_type = arguments.get("backup_type", "incremental")
            max_results = arguments.get("max_results", 1000)
            query = arguments.get("query")
            
            gmail_api = GmailAPI(credentials=credentials)
            backup_service = GmailBackup(api=gmail_api, config=config)
            
            if backup_type == "incremental":
                result = backup_service.incremental_backup(
                    user_id=user_id,
                    query=query,
                    max_results=max_results
                )
            else:
                result = backup_service.full_backup(
                    user_id=user_id,
                    query=query,
                    max_results=max_results
                )
            
            if result.success:
                return [
                    TextContent(
                        type="text",
                        text=f"Backup completed successfully!\n"
                             f"- Messages backed up: {result.message_count}\n"
                             f"- Backup path: {result.backup_path}\n"
                             f"- Messages processed: {result.messages_processed}\n"
                             f"- Messages failed: {result.messages_failed}"
                    )
                ]
            else:
                return [
                    TextContent(
                        type="text",
                        text=f"Backup failed: {result.error}"
                    )
                ]
        
        elif name == "gmail_export":
            export_format = arguments.get("format", "mbox")
            output_path = arguments.get("output_path")
            max_results = arguments.get("max_results", 100)
            query = arguments.get("query")
            
            gmail_api = GmailAPI(credentials=credentials)
            exporter = GmailExporter(api=gmail_api)
            
            result = exporter.export_messages(
                user_id=user_id,
                output_path=output_path,
                format=export_format,
                query=query,
                max_results=max_results
            )
            
            return [
                TextContent(
                    type="text",
                    text=f"Export completed successfully!\n"
                         f"- Format: {result['format']}\n"
                         f"- Messages exported: {result['message_count']}\n"
                         f"- Output path: {result['output_path']}\n"
                         f"- File size: {result.get('file_size', 0):,} bytes"
                )
            ]
        
        elif name == "gmail_list_messages":
            query = arguments.get("query")
            max_results = arguments.get("max_results", 10)
            
            gmail_api = GmailAPI(credentials=credentials)
            result = gmail_api.list_messages(
                user_id=user_id,
                query=query,
                max_results=max_results
            )
            
            messages = result.get("messages", [])
            message_list = "\n".join([
                f"- {msg.get('id', 'unknown')}: {msg.get('snippet', '')[:50]}..."
                for msg in messages[:max_results]
            ])
            
            return [
                TextContent(
                    type="text",
                    text=f"Found {len(messages)} messages:\n{message_list}"
                )
            ]
        
        elif name == "gmail_list_labels":
            gmail_api = GmailAPI(credentials=credentials)
            labels = gmail_api.list_labels(user_id=user_id)
            
            label_names = [label.get("name", "") for label in labels]
            label_list = "\n".join([f"- {name}" for name in label_names[:20]])
            
            return [
                TextContent(
                    type="text",
                    text=f"Found {len(labels)} labels:\n{label_list}"
                )
            ]
        
        elif name == "gmail_send_message":
            to = arguments.get("to")
            subject = arguments.get("subject")
            body = arguments.get("body")
            body_html = arguments.get("body_html")
            cc = arguments.get("cc")
            bcc = arguments.get("bcc")
            reply_to = arguments.get("reply_to")
            
            if not to:
                return [
                    TextContent(
                        type="text",
                        text="Error: 'to' email address is required"
                    )
                ]
            if not subject:
                return [
                    TextContent(
                        type="text",
                        text="Error: 'subject' is required"
                    )
                ]
            if not body and not body_html:
                return [
                    TextContent(
                        type="text",
                        text="Error: Either 'body' or 'body_html' is required"
                    )
                ]
            
            gmail_api = GmailAPI(credentials=credentials)
            result = gmail_api.send_message(
                user_id=user_id,
                to=to,
                subject=subject,
                body=body,
                body_html=body_html,
                cc=cc,
                bcc=bcc,
                reply_to=reply_to
            )
            
            return [
                TextContent(
                    type="text",
                    text=f"✅ Email sent successfully!\n"
                         f"- Message ID: {result.get('id', 'unknown')}\n"
                         f"- Thread ID: {result.get('threadId', 'unknown')}\n"
                         f"- To: {to}\n"
                         f"- Subject: {subject}"
                )
            ]
        
        else:
            return [
                TextContent(
                    type="text",
                    text=f"Unknown tool: {name}"
                )
            ]
    
    except Exception as e:
        return [
            TextContent(
                type="text",
                text=f"Error executing tool {name}: {str(e)}"
            )
        ]


async def main():
    """Main entry point for MCP server."""
    try:
        async with stdio_server() as (read_stream, write_stream):
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options()
            )
    except Exception as e:
        # Log to stderr so it appears in Cursor logs
        print(f"Error in MCP server: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        raise


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # Graceful shutdown
        pass
    except Exception as e:
        print(f"Fatal error in MCP server: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
