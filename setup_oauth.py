#!/usr/bin/env python3
"""
Quick setup script to help create OAuth credentials for Gmail API.

This script guides you through the OAuth setup process.
"""

import json
import webbrowser
from pathlib import Path

def print_step(step_num, description):
    print(f"\n{'='*60}")
    print(f"STEP {step_num}: {description}")
    print('='*60)

def main():
    print("""
╔══════════════════════════════════════════════════════════╗
║   Gmail MCP Server - OAuth Credentials Setup Helper     ║
╚══════════════════════════════════════════════════════════╝

This script will help you set up OAuth 2.0 credentials for Gmail API access.

What you need:
  • A Google account (personal Gmail or Google Workspace)
  • Access to Google Cloud Console (free to use)

Time required: ~3-5 minutes
""")
    
    input("Press Enter to continue...")
    
    print_step(1, "Open Google Cloud Console")
    print("\nWe'll open the Google Cloud Console in your browser.")
    print("You'll need to:")
    print("  1. Select or create a project")
    print("  2. Enable Gmail API")
    print("  3. Create OAuth credentials")
    
    response = input("\nOpen Google Cloud Console now? (y/n): ")
    if response.lower() == 'y':
        webbrowser.open("https://console.cloud.google.com/")
        print("\n✅ Browser opened!")
    
    print_step(2, "Enable Gmail API")
    print("\n1. In Google Cloud Console, go to: APIs & Services > Library")
    print("2. Search for 'Gmail API'")
    print("3. Click 'Enable'")
    
    response = input("\nOpen Gmail API page directly? (y/n): ")
    if response.lower() == 'y':
        webbrowser.open("https://console.cloud.google.com/apis/library/gmail.googleapis.com")
        print("\n✅ Browser opened!")
    
    input("\nPress Enter when Gmail API is enabled...")
    
    print_step(3, "Configure OAuth Consent Screen")
    print("\n1. Go to: APIs & Services > OAuth consent screen")
    print("2. Choose 'External' user type")
    print("3. Fill in required fields:")
    print("   - App name: 'Gmail MCP Server' (or your choice)")
    print("   - User support email: Your email")
    print("   - Developer contact: Your email")
    print("4. Click 'Save and Continue' through scopes (we'll add them)")
    print("5. Add yourself as a test user (if using External type)")
    print("6. Click 'Save and Continue' to finish")
    
    response = input("\nOpen OAuth consent screen? (y/n): ")
    if response.lower() == 'y':
        webbrowser.open("https://console.cloud.google.com/apis/credentials/consent")
        print("\n✅ Browser opened!")
    
    input("\nPress Enter when OAuth consent screen is configured...")
    
    print_step(4, "Create OAuth Client ID")
    print("\n1. Go to: APIs & Services > Credentials")
    print("2. Click '+ CREATE CREDENTIALS' > 'OAuth client ID'")
    print("3. Choose 'Desktop app' as application type")
    print("4. Name it 'Gmail MCP Server' (or your choice)")
    print("5. Click 'Create'")
    print("6. Download the JSON file")
    
    response = input("\nOpen credentials page? (y/n): ")
    if response.lower() == 'y':
        webbrowser.open("https://console.cloud.google.com/apis/credentials")
        print("\n✅ Browser opened!")
    
    input("\nPress Enter when you've downloaded the credentials JSON file...")
    
    print_step(5, "Place Credentials File")
    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)
    credentials_path = config_dir / "credentials.json"
    
    print(f"\nPlease enter the path to your downloaded credentials file.")
    print(f"It's usually in your Downloads folder.")
    print(f"\nExample: ~/Downloads/client_secret_123456789.json")
    
    downloaded_path = input("\nPath to credentials file: ").strip()
    
    # Remove quotes if present
    downloaded_path = downloaded_path.strip("'\"")
    downloaded_path = Path(downloaded_path).expanduser()
    
    # Try to find the file if exact path doesn't work
    if not downloaded_path.exists():
        # Try searching in Downloads folder
        downloads_dir = Path.home() / "Downloads"
        if downloads_dir.exists():
            matching_files = list(downloads_dir.glob("*client_secret*.json"))
            if matching_files:
                print(f"\nFound {len(matching_files)} potential credential file(s) in Downloads:")
                for i, f in enumerate(matching_files, 1):
                    print(f"  {i}. {f.name}")
                choice = input(f"\nUse file #{1 if len(matching_files) == 1 else '1-' + str(len(matching_files))}? (or enter number): ").strip()
                if choice.isdigit() and 1 <= int(choice) <= len(matching_files):
                    downloaded_path = matching_files[int(choice) - 1]
                elif len(matching_files) == 1:
                    downloaded_path = matching_files[0]
                    print(f"Using: {downloaded_path.name}")
                else:
                    print(f"\n❌ File not found: {downloaded_path}")
                    print("\nPlease check the path and try again.")
                    return
            else:
                print(f"\n❌ File not found: {downloaded_path}")
                print("\nPlease check the path and try again.")
                return
        else:
            print(f"\n❌ File not found: {downloaded_path}")
            print("\nPlease check the path and try again.")
            return
    
    # Copy to config directory
    import shutil
    shutil.copy(downloaded_path, credentials_path)
    print(f"\n✅ Credentials file copied to: {credentials_path}")
    
    # Verify it's valid JSON
    try:
        with open(credentials_path) as f:
            creds_data = json.load(f)
        if "installed" in creds_data or "web" in creds_data:
            print("✅ Credentials file looks valid!")
        else:
            print("⚠️  Warning: Credentials file structure looks unusual")
    except json.JSONDecodeError:
        print("❌ Error: File is not valid JSON")
        return
    
    print_step(6, "Done! You're Ready")
    print(f"""
✅ Setup complete!

Your credentials are saved at: {credentials_path}

Next steps:
  1. Try using the MCP server in Cursor: "List my Gmail labels"
  2. The browser will open automatically for authentication
  3. Grant Gmail permissions (one-time only)
  4. Credentials will be stored securely for future use

The OAuth flow will:
  • Reuse your existing Google login (if already logged in)
  • Only ask for Gmail permissions
  • Store credentials securely (no need to re-authenticate)

Enjoy using the Gmail MCP server! 🎉
""")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled.")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

