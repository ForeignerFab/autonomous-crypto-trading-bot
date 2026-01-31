# ⚡ Quick Discord Setup (5 Minutes)

## Fast Track Setup

### Option 1: Use Setup Script (Easiest)

```bash
cd "d:/AI TRADER/Cryptobot/okx_trading_bot"
python setup_discord.py
```

The script will:
- ✅ Guide you through each step
- ✅ Open browser links for you
- ✅ Update .env file automatically
- ✅ Test the connection

### Option 2: Manual Setup (5 Steps)

#### 1. Create Bot (2 min)
- Go to: https://discord.com/developers/applications
- New Application → "OKX Trading Bot"
- Bot → Add Bot
- Enable "Message Content Intent" ✅
- Copy token

#### 2. Invite Bot (1 min)
- OAuth2 → URL Generator
- Check: `bot` and `applications.commands`
- Check permissions: Send Messages, Embed Links, Attach Files
- Copy URL → Open → Select server → Authorize

#### 3. Get Channel ID (30 sec)
- Discord Settings → Advanced → Developer Mode ON
- Right-click channel → Copy ID

#### 4. Update .env (30 sec)
Open `.env` file and add:
```env
DISCORD_BOT_TOKEN=your_token_here
DISCORD_CHANNEL_ID=your_channel_id_here
```

#### 5. Test (1 min)
```bash
python main.py
```

Check Discord - bot should be online!

---

## What You'll Get

Once setup, Discord will show:
- ✅ Trade notifications (buy/sell)
- ✅ Position updates
- ✅ Daily reports
- ✅ Error alerts
- ✅ Bot commands (!status, !balance, etc.)

---

## Need Detailed Steps?

See: `DISCORD_SETUP_WALKTHROUGH.md` for complete guide with screenshots.

---

## Troubleshooting

**Bot not online?**
- Check token is correct
- Check bot is invited to server
- Check logs: `tail logs/trading_bot.log`

**Commands not working?**
- Enable "Message Content Intent" in Developer Portal
- Re-invite bot with correct permissions

---

## ✅ Ready!

Once Discord is set up, you're ready to start trading!








