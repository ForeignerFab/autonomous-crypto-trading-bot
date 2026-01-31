#!/usr/bin/env python3
"""
Interactive Discord Setup Script
Walks you through Discord bot creation and configuration
"""

import os
import webbrowser
from pathlib import Path

def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")

def print_step(number, title):
    """Print step header"""
    print(f"\n{'='*60}")
    print(f"STEP {number}: {title}")
    print('='*60 + "\n")

def setup_discord():
    """Interactive Discord setup"""
    
    print_header("Discord Integration Setup")
    print("This script will guide you through Discord bot setup.")
    print("Time required: 10-15 minutes\n")
    
    input("Press Enter to continue...")
    
    # Step 1: Create Server
    print_step(1, "Create Discord Server")
    print("1. Open Discord (https://discord.com or app)")
    print("2. Click '+' icon → 'Create My Own' → 'For me and my friends'")
    print("3. Name it: 'Crypto Trading Bot' (or any name)")
    print("4. Create a channel (e.g., #trading-bot)")
    print()
    input("Press Enter when your server is created...")
    
    # Step 2: Developer Portal
    print_step(2, "Create Discord Bot")
    print("Opening Discord Developer Portal...")
    print()
    
    dev_portal = "https://discord.com/developers/applications"
    print(f"1. Go to: {dev_portal}")
    print("2. Click 'New Application'")
    print("3. Name it: 'OKX Trading Bot'")
    print("4. Click 'Create'")
    print()
    
    open_browser = input("Open Developer Portal in browser? (y/n): ").lower()
    if open_browser == 'y':
        webbrowser.open(dev_portal)
    
    input("\nPress Enter when you've created the application...")
    
    # Step 3: Bot Configuration
    print_step(3, "Configure Bot")
    print("In Developer Portal:")
    print("1. Click 'Bot' in left sidebar")
    print("2. Click 'Add Bot' → 'Yes, do it!'")
    print("3. Set username: 'OKX-Trader'")
    print("4. Turn OFF 'Public Bot'")
    print("5. Scroll down to 'Privileged Gateway Intents':")
    print("   ✅ Enable 'Message Content Intent' (REQUIRED)")
    print("   ✅ Enable 'Presence Intent' (optional)")
    print("6. Click 'Save Changes'")
    print()
    input("Press Enter when bot is configured...")
    
    # Step 4: Get Token
    print_step(4, "Get Bot Token")
    print("In Developer Portal → Bot section:")
    print("1. Find 'Token' section")
    print("2. Click 'Reset Token' (for security)")
    print("3. Confirm any prompts")
    print("4. Click 'Copy' to copy token")
    print()
    
    bot_token = input("Paste your bot token here: ").strip()
    
    if not bot_token or len(bot_token) < 50:
        print("❌ Invalid token. Please try again.")
        return False
    
    print("✅ Token received!")
    
    # Step 5: Invite Bot
    print_step(5, "Invite Bot to Server")
    print("In Developer Portal:")
    print("1. Click 'OAuth2' → 'URL Generator'")
    print("2. Under 'Scopes', check:")
    print("   ✅ bot")
    print("   ✅ applications.commands")
    print("3. Under 'Bot Permissions', check:")
    print("   ✅ Send Messages")
    print("   ✅ Embed Links")
    print("   ✅ Attach Files")
    print("   ✅ Read Message History")
    print("   ✅ Use Slash Commands")
    print("4. Copy the generated URL at bottom")
    print()
    
    invite_url = input("Paste the invite URL here (or press Enter to skip): ").strip()
    
    if invite_url:
        open_invite = input("Open invite URL in browser? (y/n): ").lower()
        if open_invite == 'y':
            webbrowser.open(invite_url)
        print("\n✅ Select your server and authorize the bot!")
        input("Press Enter when bot is invited to your server...")
    
    # Step 6: Get Channel ID
    print_step(6, "Get Channel ID")
    print("In Discord:")
    print("1. Go to User Settings (gear icon) → Advanced")
    print("2. Turn ON 'Developer Mode'")
    print("3. Go to your server")
    print("4. Right-click the channel you want to use")
    print("5. Click 'Copy ID'")
    print()
    
    channel_id = input("Paste your channel ID here: ").strip()
    
    if not channel_id or not channel_id.isdigit():
        print("❌ Invalid channel ID. Please try again.")
        return False
    
    print("✅ Channel ID received!")
    
    # Step 7: Update .env file
    print_step(7, "Update Configuration")
    
    env_path = Path(__file__).parent / ".env"
    
    # Read existing .env if it exists
    env_content = ""
    if env_path.exists():
        with open(env_path, 'r') as f:
            env_content = f.read()
    else:
        # Create from template
        template_path = Path(__file__).parent / "ENV_FILE_CONTENT.txt"
        if template_path.exists():
            with open(template_path, 'r') as f:
                env_content = f.read()
    
    # Update Discord credentials
    lines = env_content.split('\n')
    updated_lines = []
    
    for line in lines:
        if line.startswith('DISCORD_BOT_TOKEN='):
            updated_lines.append(f'DISCORD_BOT_TOKEN={bot_token}')
        elif line.startswith('DISCORD_CHANNEL_ID='):
            updated_lines.append(f'DISCORD_CHANNEL_ID={channel_id}')
        else:
            updated_lines.append(line)
    
    # Write updated .env
    try:
        with open(env_path, 'w') as f:
            f.write('\n'.join(updated_lines))
        
        # Set permissions (Unix)
        if os.name != 'nt':
            os.chmod(env_path, 0o600)
        
        print(f"✅ Updated .env file: {env_path}")
        print()
        print("Discord credentials added:")
        print(f"  Bot Token: {bot_token[:20]}...")
        print(f"  Channel ID: {channel_id}")
        print()
        
    except Exception as e:
        print(f"❌ Error updating .env file: {e}")
        print("\nManual update needed:")
        print(f"  DISCORD_BOT_TOKEN={bot_token}")
        print(f"  DISCORD_CHANNEL_ID={channel_id}")
        return False
    
    # Step 8: Test
    print_step(8, "Test Connection")
    print("Ready to test! Next steps:")
    print()
    print("1. Start the bot:")
    print("   python main.py")
    print()
    print("2. Check Discord:")
    print("   - Bot should appear online")
    print("   - You should see: '🤖 Trading Bot Connected'")
    print()
    print("3. Test commands in Discord:")
    print("   !status")
    print("   !balance")
    print()
    
    test_now = input("Test now? (y/n): ").lower()
    if test_now == 'y':
        print("\nStarting bot... (Press Ctrl+C to stop)")
        print("=" * 60)
        try:
            import subprocess
            import sys
            subprocess.run([sys.executable, "main.py"])
        except KeyboardInterrupt:
            print("\n\nBot stopped.")
        except Exception as e:
            print(f"\nError: {e}")
            print("\nYou can test manually with: python main.py")
    
    print_header("Discord Setup Complete!")
    print("✅ Discord integration configured!")
    print("✅ Bot token added to .env")
    print("✅ Channel ID configured")
    print()
    print("Next: Start bot with 'python main.py'")
    
    return True

if __name__ == "__main__":
    import sys
    try:
        success = setup_discord()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

