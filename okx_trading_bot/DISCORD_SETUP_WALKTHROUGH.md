# 🎮 Discord Integration - Step-by-Step Walkthrough

## Overview

This guide will walk you through setting up Discord integration for your trading bot. Discord will send you:
- ✅ Real-time trade notifications
- ✅ Daily performance reports
- ✅ Error alerts
- ✅ Bot status updates
- ✅ Interactive commands (!status, !balance, !positions, !report)

**Time Required:** 10-15 minutes

---

## Step 1: Create Discord Server (2 minutes)

### 1.1 Open Discord

1. Go to https://discord.com or open Discord app
2. Log in to your account

### 1.2 Create New Server

1. Click the **"+"** icon in the left sidebar (or "Add a Server")
2. Click **"Create My Own"**
3. Select **"For me and my friends"**
4. Name your server: **"Crypto Trading Bot"** (or any name you like)
5. Click **"Create"**

### 1.3 Create Channels

Right-click your server name → **"Create Channel"** → Create these:

1. **#trades** - For trade notifications
2. **#alerts** - For warnings and alerts  
3. **#reports** - For daily reports
4. **#bot-commands** - For bot commands

**Quick Tip:** You can use one channel for everything if you prefer (e.g., just #trading-bot)

---

## Step 2: Create Discord Bot (5 minutes)

### 2.1 Go to Developer Portal

1. Visit: https://discord.com/developers/applications
2. Log in with your Discord account

### 2.2 Create New Application

1. Click **"New Application"** (top-right)
2. Name it: **"OKX Trading Bot"**
3. Click **"Create"**

### 2.3 Create Bot User

1. In left sidebar, click **"Bot"**
2. Click **"Add Bot"**
3. Click **"Yes, do it!"** to confirm

### 2.4 Configure Bot

1. **Username:** Change to "OKX-Trader" (or keep default)
2. **Public Bot:** Turn OFF (uncheck) - This is private
3. **Requires OAuth2 Code Grant:** Turn OFF (uncheck)

### 2.5 Enable Intents (IMPORTANT!)

Scroll down to **"Privileged Gateway Intents"**:

- ✅ **Message Content Intent** - MUST be enabled (for commands)
- ✅ **Presence Intent** - Optional (for status)
- ✅ **Server Members Intent** - Optional (for member info)

**Click "Save Changes"**

### 2.6 Get Bot Token

1. In the **"Token"** section, click **"Reset Token"**
2. Confirm any security prompts
3. Click **"Copy"** to copy the token
4. **SAVE THIS TOKEN** - You'll need it in Step 4

**⚠️ IMPORTANT:** Never share this token publicly!

---

## Step 3: Invite Bot to Your Server (2 minutes)

### 3.1 Generate Invite Link

1. In left sidebar, click **"OAuth2"** → **"URL Generator"**

### 3.2 Select Scopes

Check these boxes:
- ✅ **bot**
- ✅ **applications.commands**

### 3.3 Select Bot Permissions

Check these permissions:
- ✅ **Send Messages**
- ✅ **Embed Links**
- ✅ **Attach Files**
- ✅ **Read Message History**
- ✅ **Use Slash Commands**
- ✅ **Manage Messages**

### 3.4 Copy Invite URL

1. Scroll down - you'll see a URL at the bottom
2. **Copy this URL**

### 3.5 Invite Bot

1. **Paste the URL** in your browser
2. Select your **"Crypto Trading Bot"** server from dropdown
3. Click **"Authorize"**
4. Complete any CAPTCHA if prompted

### 3.6 Verify Bot Joined

1. Go back to your Discord server
2. Check member list - you should see your bot (offline for now)
3. ✅ Bot is now in your server!

---

## Step 4: Get Channel ID (1 minute)

### 4.1 Enable Developer Mode

1. In Discord, go to **User Settings** (gear icon)
2. Go to **"Advanced"**
3. Turn ON **"Developer Mode"**

### 4.2 Get Channel ID

1. Go to your Discord server
2. Right-click on the channel you want to use (e.g., #trades)
3. Click **"Copy ID"**
4. **SAVE THIS ID** - You'll need it next

**Note:** If you don't see "Copy ID", make sure Developer Mode is enabled!

---

## Step 5: Update .env File (2 minutes)

### 5.1 Open .env File

Navigate to your bot folder and open `.env` file:
```bash
cd "d:/AI TRADER/Cryptobot/okx_trading_bot"
notepad .env
```

### 5.2 Add Discord Credentials

Find these lines in your `.env` file:
```env
DISCORD_BOT_TOKEN=
DISCORD_CHANNEL_ID=
```

Replace with:
```env
DISCORD_BOT_TOKEN=YOUR_BOT_TOKEN_HERE
DISCORD_CHANNEL_ID=YOUR_CHANNEL_ID_HERE
```

**Example:**
```env
DISCORD_BOT_TOKEN=YOUR_BOT_TOKEN_HERE
DISCORD_CHANNEL_ID=YOUR_CHANNEL_ID_HERE
```

### 5.3 Save File

Save the `.env` file

---

## Step 6: Test Discord Integration (2 minutes)

### 6.1 Start the Bot

```bash
cd "d:/AI TRADER/Cryptobot/okx_trading_bot"
python main.py
```

### 6.2 Check Discord

1. Go to your Discord server
2. Bot should appear **online** (green dot)
3. You should see a message: **"🤖 Trading Bot Connected"**

### 6.3 Test Commands

In your Discord channel, try these commands:

```
!status
!balance
!positions
!report
```

Bot should respond to each command!

---

## Step 7: Verify Everything Works

### ✅ Checklist

- [ ] Bot appears online in Discord
- [ ] Bot sent "Trading Bot Connected" message
- [ ] `!status` command works
- [ ] `!balance` command works
- [ ] Bot logs show "Discord bot connected"

### 🎉 Success!

If all checks pass, Discord integration is complete!

---

## Troubleshooting

### Bot Not Appearing Online

**Check:**
1. Bot token is correct in `.env`
2. Bot is invited to server
3. Check bot logs for errors

**Fix:**
```bash
# Check .env file
cat .env | grep DISCORD

# Check logs
tail -20 logs/trading_bot.log
```

### Bot Not Responding to Commands

**Check:**
1. Message Content Intent is enabled (Step 2.5)
2. Bot has "Send Messages" permission
3. Channel ID is correct

**Fix:**
- Re-enable Message Content Intent in Developer Portal
- Re-invite bot with correct permissions

### "Invalid Token" Error

**Check:**
1. Token copied correctly (no extra spaces)
2. Token hasn't been reset
3. Token is in `.env` file

**Fix:**
- Get new token from Developer Portal
- Update `.env` file

---

## Optional: Webhook Setup (Alternative)

If you prefer webhooks over bot:

1. Go to channel settings → **Integrations** → **Webhooks**
2. Click **"New Webhook"**
3. Copy webhook URL
4. Add to `.env`:
   ```env
   DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
   ```

---

## Next Steps

Once Discord is working:

1. ✅ Test all commands
2. ✅ Monitor trade notifications
3. ✅ Check daily reports
4. ✅ Set up Ollama AI (optional)
5. ✅ Deploy to cloud (optional)

---

## Quick Reference

**Discord Developer Portal:** https://discord.com/developers/applications  
**Your Server:** Your Discord server  
**Bot Token:** From Developer Portal → Bot → Token  
**Channel ID:** Right-click channel → Copy ID (Developer Mode required)

---

## 🎉 You're Done!

Your Discord integration is now complete. The bot will send you notifications for all trades, alerts, and daily reports!








