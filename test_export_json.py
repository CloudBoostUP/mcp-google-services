#!/usr/bin/env python3
"""Test script to export Gmail messages to JSON."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from mcp_google_services.utils.config import Config
from mcp_google_services.core.auth import AuthManager
from mcp_google_services.services.gmail.api import GmailAPI
from mcp_google_services.services.gmail.export import GmailExporter


def main():
    print("🔐 Authenticating...")
    config = Config()
    auth_manager = AuthManager(config=config)
    
    try:
        credentials = auth_manager.get_credentials("me")
        print("✅ Authentication successful!")
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return
    
    print("\n📧 Exporting Gmail messages to JSON...")
    gmail_api = GmailAPI(credentials=credentials)
    exporter = GmailExporter(api=gmail_api)
    
    try:
        print("Exporting messages (max 10 for testing)...")
        print("This may take a moment...\n")
        
        result = exporter.export_messages(
            user_id="me",
            format="json",
            max_results=10
        )
        
        print("✅ Export completed successfully!\n")
        print(f"📊 Summary:")
        print(f"   • Messages exported: {result['message_count']}")
        print(f"   • Output path: {result['output_path']}")
        
        if result.get("file_size"):
            file_size = result["file_size"]
            print(f"   • File size: {file_size:,} bytes ({file_size / 1024:.2f} KB)")
        
        # Check file exists and show preview
        output_path = Path(result["output_path"])
        if output_path.exists():
            print(f"\n📄 JSON file created successfully!")
            
            # Show preview of JSON structure
            import json
            with open(output_path, 'r') as f:
                data = json.load(f)
                print(f"   • Total messages in JSON: {len(data) if isinstance(data, list) else 1}")
                if isinstance(data, list) and len(data) > 0:
                    first_msg = data[0]
                    print(f"   • Sample fields: {', '.join(list(first_msg.keys())[:5])}...")
                    print(f"\n   📝 Sample message preview:")
                    print(f"      Subject: {first_msg.get('subject', 'N/A')[:60]}")
                    print(f"      From: {first_msg.get('from', 'N/A')[:50]}")
                    print(f"      Date: {first_msg.get('date', 'N/A')}")
        else:
            print(f"\n⚠️  Warning: Output file not found at {output_path}")
            
    except Exception as e:
        print(f"❌ Error during export: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

