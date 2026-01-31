# 🎮 Discord Setup - Visual Step-by-Step Guide

## Quick Start (Choose One)

### 🚀 Option 1: Automated Setup (Recommended)
```bash
cd "d:/AI TRADER/Cryptobot/okx_trading_bot"
python setup_discord.py
```
**This will guide you through everything interactively!**

### 📖 Option 2: Manual Setup
Follow the steps below

---

## Step-by-Step Visual Guide

### STEP 1: Create Discord Server ⏱️ 2 minutes

```
1. Open Discord (app or web)
   ↓
2. Click "+" icon (left sidebar)
   ↓
3. "Create My Own" → "For me and my friends"
   ↓
4. Name: "Crypto Trading Bot"
   ↓
5. Create a channel: #trading-bot
```

**✅ Done when:** You have a Discord server with at least one channel

---

### STEP 2: Create Bot Application ⏱️ 3 minutes

```
1. Go to: https://discord.com/developers/applications
   ↓
2. Click "New Application" (top-right)
   ↓
3. Name: "OKX Trading Bot"
   ↓
4. Click "Create"
   ↓
5. Left sidebar → Click "Bot"
   ↓
6. Click "Add Bot" → "Yes, do it!"
   ↓
7. Scroll down to "Privileged Gateway Intents"
   ↓
8. ✅ CHECK "Message Content Intent" (REQUIRED!)
   ↓
9. Click "Save Changes"
```

**✅ Done when:** Bot is created and Message Content Intent is enabled

---

### STEP 3: Get Bot Token ⏱️ 1 minute

```
In Developer Portal → Bot section:

1. Find "Token" section
   ↓
2. Click "Reset Token"
   ↓
3. Confirm prompts
   ↓
4. Click "Copy"
   ↓
5. SAVE THIS TOKEN! (You'll paste it in Step 6)
```

**Token looks like:** `YOUR_BOT_TOKEN_HERE`

**✅ Done when:** You have copied the token

---

### STEP 4: Invite Bot to Server ⏱️ 2 minutes

```
In Developer Portal:

1. Left sidebar → "OAuth2" → "URL Generator"
   ↓
2. Under "Scopes", check:
   ✅ bot
   ✅ applications.commands
   ↓
3. Scroll down to "Bot Permissions", check:
   ✅ Send Messages
   ✅ Embed Links
   ✅ Attach Files
   ✅ Read Message History
   ✅ Use Slash Commands
   ↓
4. Copy the URL at bottom
   ↓
5. Paste URL in browser
   ↓
6. Select your server
   ↓
7. Click "Authorize"
   ↓
8. Complete CAPTCHA if needed
```

**✅ Done when:** Bot appears in your server member list

---

### STEP 5: Get Channel ID ⏱️ 1 minute

```
In Discord:

1. Click your profile (bottom left)
   ↓
2. "User Settings" (gear icon)
   ↓
3. "Advanced" (left sidebar)
   ↓
4. Turn ON "Developer Mode"
   ↓
5. Go back to your server
   ↓
6. Right-click the channel you want
   ↓
7. Click "Copy ID"
   ↓
8. SAVE THIS ID! (You'll paste it in Step 6)
```

**Channel ID looks like:** `1234567890123456789` (long number)

**✅ Done when:** You have copied the channel ID

---

### STEP 6: Update .env File ⏱️ 1 minute

**Option A: Use Setup Script**
```bash
cd "d:/AI TRADER/Cryptobot/okx_trading_bot"
python setup_discord.py
```
(It will ask for token and channel ID)

**Option B: Manual Edit**

1. Open `.env` file in `okx_trading_bot` folder
2. Find these lines:
   ```env
   DISCORD_BOT_TOKEN=
   DISCORD_CHANNEL_ID=
   ```
3. Replace with:
   ```env
   DISCORD_BOT_TOKEN=YOUR_TOKEN_HERE
   DISCORD_CHANNEL_ID=YOUR_CHANNEL_ID_HERE
   ```
4. Save file

**✅ Done when:** .env file has both values filled in

---

### STEP 7: Test! ⏱️ 2 minutes

```bash
cd "d:/AI TRADER/Cryptobot/okx_trading_bot"
python main.py
```

**Check Discord:**
- ✅ Bot appears **online** (green dot)
- ✅ Message appears: "🤖 Trading Bot Connected"

**Test Commands in Discord:**
```
!status
!balance
!positions
```

**✅ Done when:** Bot responds to commands!

---

## 🎉 Success Checklist

- [ ] Bot appears online in Discord
- [ ] "Trading Bot Connected" message received
- [ ] `!status` command works
- [ ] `!balance` command works
- [ ] No errors in bot logs

---

## 🐛 Troubleshooting

### Bot Not Online?

**Check:**
1. Token correct in `.env`?
2. Bot invited to server?
3. Check logs: `tail logs/trading_bot.log`

**Fix:**
- Verify token (no extra spaces)
- Re-invite bot if needed

### Commands Not Working?

**Check:**
1. Message Content Intent enabled? (Step 2)
2. Bot has "Send Messages" permission?
3. Channel ID correct?

**Fix:**
- Re-enable Message Content Intent
- Re-invite bot with permissions

### "Invalid Token" Error?

**Check:**
1. Token copied correctly?
2. No extra spaces?
3. Token not reset?

**Fix:**
- Get new token from Developer Portal
- Update `.env` file

---

## 📝 Quick Reference

| Item | Where to Find |
|------|---------------|
| **Developer Portal** | https://discord.com/developers/applications |
| **Bot Token** | Developer Portal → Your App → Bot → Token |
| **Invite URL** | Developer Portal → OAuth2 → URL Generator |
| **Channel ID** | Right-click channel → Copy ID (Developer Mode ON) |

---

## ⏱️ Total Time: 10-15 minutes

**Ready?** Start with Step 1 or run `python setup_discord.py`!








