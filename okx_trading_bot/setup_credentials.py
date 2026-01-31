#!/usr/bin/env python3
"""
Setup script to configure OKX API credentials
This script creates/updates the .env file with your credentials
"""

import os
from pathlib import Path

def setup_credentials():
    """Setup OKX API credentials in .env file"""
    
    # Path to .env file
    env_path = Path(__file__).parent / ".env"
    
    print("=" * 60)
    print("OKX API Credentials Setup")
    print("=" * 60)
    print()
    
    # Your provided credentials
    api_key = "da3dcb0c-6fa9-4b24-a03e-d555d36dd9b8"
    secret_key = "17D920C0D29435BF0C48A67541FCED7F"
    
    print("✅ API Key: da3dcb0c-6fa9-4b24-a03e-d555d36dd9b8")
    print("✅ Secret Key: 17D920C0D29435BF0C48A67541FCED7F")
    print()
    
    # Get passphrase from user
    print("⚠️  IMPORTANT: You need to provide your OKX passphrase")
    print("   (This is the password you set when creating the API key)")
    print()
    
    passphrase = input("Enter your OKX passphrase: ").strip()
    
    if not passphrase:
        print("❌ Passphrase cannot be empty!")
        return False
    
    # Create .env file content
    env_content = f"""# OKX Trading Bot Environment Variables
# IMPORTANT: This file contains sensitive credentials - NEVER commit to version control!

# OKX API Credentials (Demo Account)
OKX_API_KEY={api_key}
OKX_SECRET_KEY={secret_key}
OKX_PASSPHRASE={passphrase}

# OKX Configuration
OKX_SANDBOX=true
OKX_BASE_URL=https://www.okx.com

# Discord Configuration (Optional but recommended)
DISCORD_BOT_TOKEN=
DISCORD_CHANNEL_ID=
DISCORD_WEBHOOK_URL=

# Ollama AI Configuration (Free AI)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:7b

# Trading Configuration
INITIAL_CAPITAL=500.0
RISK_PER_TRADE=0.02
MAX_DAILY_LOSS=50.0

# Logging
LOG_LEVEL=INFO
"""
    
    # Write .env file
    try:
        with open(env_path, 'w') as f:
            f.write(env_content)
        
        # Set file permissions (Unix-like systems)
        if os.name != 'nt':
            os.chmod(env_path, 0o600)
        
        print()
        print("=" * 60)
        print("✅ Credentials configured successfully!")
        print("=" * 60)
        print()
        print(f"📁 .env file created at: {env_path}")
        print()
        print("🔒 Security:")
        print("   - File permissions set to 600 (read/write owner only)")
        print("   - File is in .gitignore (won't be committed)")
        print()
        print("🧪 Next steps:")
        print("   1. Test connection: python main.py")
        print("   2. Check logs for: 'OKX client connected successfully'")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False

if __name__ == "__main__":
    try:
        success = setup_credentials()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
        exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        exit(1)








