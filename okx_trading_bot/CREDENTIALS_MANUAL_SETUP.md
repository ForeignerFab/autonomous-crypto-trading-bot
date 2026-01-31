# 🔑 Manual Credentials Setup Guide

## Your OKX Demo Account Credentials

I've prepared your credentials. You need to create the `.env` file manually since it's protected for security.

### Your Credentials

**API Key:** `da3dcb0c-6fa9-4b24-a03e-d555d36dd9b8`  
**Secret Key:** `17D920C0D29435BF0C48A67541FCED7F`  
**Passphrase:** ⚠️ **You need to provide this** (set when creating API key)

## Quick Setup (Choose One Method)

### Method 1: Use Setup Script (Easiest)

```bash
cd "d:/AI TRADER/Cryptobot/okx_trading_bot"
python setup_credentials.py
```

The script will:
- ✅ Add your API key and secret key automatically
- ⚠️ Ask you to enter your passphrase
- ✅ Create `.env` file with proper permissions

### Method 2: Manual Creation

1. **Navigate to bot directory:**
   ```bash
   cd "d:/AI TRADER/Cryptobot/okx_trading_bot"
   ```

2. **Create `.env` file:**
   ```bash
   # Windows (PowerShell)
   notepad .env
   
   # Or use any text editor
   ```

3. **Copy and paste this content:**
   ```env
   # OKX Trading Bot Environment Variables
   # IMPORTANT: This file contains sensitive credentials - NEVER commit to version control!

   # OKX API Credentials (Demo Account)
   OKX_API_KEY=da3dcb0c-6fa9-4b24-a03e-d555d36dd9b8
   OKX_SECRET_KEY=17D920C0D29435BF0C48A67541FCED7F
   OKX_PASSPHRASE=YOUR_PASSPHRASE_HERE
   # ⚠️ REPLACE YOUR_PASSPHRASE_HERE with your actual passphrase!

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
   ```

4. **Replace `YOUR_PASSPHRASE_HERE`** with your actual OKX passphrase

5. **Save the file**

## ✅ Verification

After creating `.env` file, test the connection:

```bash
python main.py
```

You should see:
```
✅ OKX client connected successfully. Available balance: X USDT
```

## 🔒 Security Confirmed

- ✅ `.env` file is in `.gitignore` - Won't be committed
- ✅ Credentials stored locally only
- ✅ Demo account (sandbox mode) - Safe for testing

## ⚠️ Important Notes

1. **Passphrase Required**: The bot won't work without your OKX passphrase
2. **Demo Account**: Currently configured for demo/sandbox mode
3. **Never Share**: Keep your `.env` file private
4. **Backup**: Consider backing up `.env` securely (encrypted)

## 🎯 What's Already Configured

- ✅ API Key: Added
- ✅ Secret Key: Added  
- ✅ Sandbox Mode: Enabled (demo account)
- ✅ Config File: Created (`config.yml`)
- ✅ Git Ignore: `.env` protected

## 🚀 Ready to Test

Once you've set your passphrase in `.env`:
```bash
python main.py
```

The bot will connect to OKX demo account and start trading!








