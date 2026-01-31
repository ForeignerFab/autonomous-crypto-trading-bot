
# Discord Integration Guide for OKX Trading Bot

This guide walks you through setting up Discord integration for your trading bot, including creating a Discord server, bot application, and configuring notifications for trades, alerts, and daily reports.

## Overview

Your trading bot will use Discord to:
- Send real-time trade notifications
- Provide daily performance reports
- Alert you to important market conditions
- Allow basic bot control commands
- Share daily PDF reports

## AI Config Suggestions (Approval Flow)

The bot can post AI-driven **config-only** suggestions (safe parameter updates).
You can approve or reject them directly in Discord:

- `!optimize` — trigger a new AI suggestion batch now
- `!suggestions` — list pending suggestion IDs
- `!approve <id>` — apply the config updates in `config.yml`
- `!reject <id>` — discard a suggestion batch

Only administrators can approve or reject config changes.

## Step 1: Create Discord Server

### Create Your Trading Server

1. **Open Discord**
   - Launch Discord desktop app or visit https://discord.com
   - Log in to your Discord account

2. **Create New Server**
   - Click the "+" icon in the left sidebar
   - Select "Create My Own"
   - Choose "For me and my friends"
   - Name your server (e.g., "Crypto Trading Bot")
   - Upload a server icon (optional)
   - Click "Create"

3. **Set Up Channels**
   Create the following text channels:
   - `#trades` - For trade execution notifications
   - `#alerts` - For market alerts and warnings
   - `#reports` - For daily performance reports
   - `#bot-commands` - For bot control commands
   - `#logs` - For system logs and errors

### Configure Channel Permissions

1. **Right-click each channel** → "Edit Channel"
2. **Go to Permissions tab**
3. **Set permissions for @everyone role:**
   - View Channel: ✅
   - Send Messages: ❌ (except #bot-commands)
   - Read Message History: ✅

## Step 2: Create Discord Bot Application

### Access Developer Portal

1. **Visit Discord Developer Portal**
   - Go to https://discord.com/developers/applications
   - Log in with your Discord account

2. **Create New Application**
   - Click "New Application" button (top-right)
   - Enter application name: "OKX Trading Bot"
   - Click "Create"

### Configure Bot Settings

1. **Navigate to Bot Section**
   - In left sidebar, click "Bot"
   - Click "Add Bot"
   - Confirm by clicking "Yes, do it!"

2. **Configure Bot Properties**
   - **Username**: Change to "OKX-Trader" or similar
   - **Avatar**: Upload a trading-related image
   - **Public Bot**: Disable (uncheck)
   - **Requires OAuth2 Code Grant**: Disable (uncheck)

3. **Enable Privileged Gateway Intents**
   Scroll down to "Privileged Gateway Intents":
   - ✅ **Presence Intent** (if you want status updates)
   - ✅ **Server Members Intent** (if you want member info)
   - ✅ **Message Content Intent** (required for commands)

4. **Save Changes**
   - Click "Save Changes" at the bottom

### Get Bot Token

1. **Reset Token** (for security)
   - In the "Token" section, click "Reset Token"
   - Confirm any 2FA prompts
   - Click "Copy" to copy the token

2. **Secure Your Token**
   - **NEVER share this token publicly**
   - **NEVER commit it to version control**
   - Store it securely (we'll use it in configuration)

## Step 3: Generate Bot Invite Link

### Configure OAuth2 Permissions

1. **Navigate to OAuth2 → URL Generator**
   - In left sidebar: OAuth2 → URL Generator

2. **Select Scopes**
   - ✅ `bot`
   - ✅ `applications.commands` (for slash commands)

3. **Select Bot Permissions**
   Required permissions:
   - ✅ **Send Messages**
   - ✅ **Embed Links**
   - ✅ **Attach Files**
   - ✅ **Read Message History**
   - ✅ **Use Slash Commands**
   - ✅ **Manage Messages** (for cleanup)

4. **Copy Generated URL**
   - Copy the URL from the bottom of the page

### Invite Bot to Your Server

1. **Open Invite Link**
   - Paste the URL in your browser
   - Select your trading server from dropdown
   - Click "Authorize"
   - Complete any CAPTCHA verification

2. **Verify Bot Joined**
   - Check your Discord server
   - Bot should appear in member list (offline initially)

## Step 4: Configure Bot in Trading System

### Create Discord Configuration File

1. **Navigate to Bot Directory**
   ```bash
   cd ~/okx_trading_bot
   ```

2. **Create Discord Config**
   ```bash
   nano config/discord_config.py
   ```

3. **Add Configuration**
   ```python
   # Discord Bot Configuration
   DISCORD_CONFIG = {
       'token': 'YOUR_BOT_TOKEN_HERE',
       'guild_id': 'YOUR_SERVER_ID_HERE',
       'channels': {
           'trades': 'TRADES_CHANNEL_ID',
           'alerts': 'ALERTS_CHANNEL_ID', 
           'reports': 'REPORTS_CHANNEL_ID',
           'commands': 'BOT_COMMANDS_CHANNEL_ID',
           'logs': 'LOGS_CHANNEL_ID'
       },
       'notifications': {
           'trade_execution': True,
           'profit_loss': True,
           'daily_summary': True,
           'error_alerts': True,
           'market_alerts': True
       },
       'report_schedule': '09:00',  # Daily report time (UTC)
       'max_message_length': 2000,
       'embed_color': 0x00ff00,  # Green for profits
       'error_color': 0xff0000   # Red for losses/errors
   }
   ```

### Get Channel and Server IDs

1. **Enable Developer Mode**
   - Discord Settings → Advanced → Developer Mode: ON

2. **Get Server ID**
   - Right-click your server name → "Copy Server ID"
   - Paste into `guild_id` in config

3. **Get Channel IDs**
   - Right-click each channel → "Copy Channel ID"
   - Paste into respective channel IDs in config

### Set Up Environment Variables

1. **Create Environment File**
   ```bash
   nano .env
   ```

2. **Add Discord Token**
   ```bash
   # Discord Configuration
   DISCORD_BOT_TOKEN=your_actual_bot_token_here
   DISCORD_GUILD_ID=your_server_id_here
   DISCORD_TRADES_CHANNEL=your_trades_channel_id
   DISCORD_ALERTS_CHANNEL=your_alerts_channel_id
   DISCORD_REPORTS_CHANNEL=your_reports_channel_id
   DISCORD_COMMANDS_CHANNEL=your_commands_channel_id
   DISCORD_LOGS_CHANNEL=your_logs_channel_id
   ```

## Step 5: Test Discord Integration

### Install Discord.py Library

```bash
# Activate virtual environment
source venv/bin/activate

# Install discord.py
pip install discord.py
```

### Create Test Script

1. **Create Test File**
   ```bash
   nano test_discord.py
   ```

2. **Add Test Code**
   ```python
   import discord
   import asyncio
   import os
   from dotenv import load_dotenv
   
   load_dotenv()
   
   class TestBot(discord.Client):
       async def on_ready(self):
           print(f'Bot connected as {self.user}')
           
           # Test sending message to trades channel
           channel = self.get_channel(int(os.getenv('DISCORD_TRADES_CHANNEL')))
           if channel:
               embed = discord.Embed(
                   title="🤖 Bot Test",
                   description="Discord integration test successful!",
                   color=0x00ff00
               )
               embed.add_field(name="Status", value="✅ Connected", inline=True)
               embed.add_field(name="Time", value=f"<t:{int(asyncio.get_event_loop().time())}:F>", inline=True)
               
               await channel.send(embed=embed)
               print("Test message sent successfully!")
           
           await self.close()
   
   # Run test
   intents = discord.Intents.default()
   intents.message_content = True
   
   client = TestBot(intents=intents)
   client.run(os.getenv('DISCORD_BOT_TOKEN'))
   ```

3. **Run Test**
   ```bash
   python test_discord.py
   ```

4. **Verify Success**
   - Check your #trades channel for the test message
   - Bot should appear online briefly

## Step 6: Configure Notification Templates

### Create Notification Templates

1. **Create Templates File**
   ```bash
   nano src/discord_templates.py
   ```

2. **Add Message Templates**
   ```python
   import discord
   from datetime import datetime
   
   class DiscordTemplates:
       @staticmethod
       def trade_execution(trade_data):
           """Template for trade execution notifications"""
           color = 0x00ff00 if trade_data['side'] == 'buy' else 0xff6b6b
           
           embed = discord.Embed(
               title=f"{'🟢 BUY' if trade_data['side'] == 'buy' else '🔴 SELL'} Order Executed",
               color=color,
               timestamp=datetime.utcnow()
           )
           
           embed.add_field(name="Symbol", value=trade_data['symbol'], inline=True)
           embed.add_field(name="Size", value=f"{trade_data['size']}", inline=True)
           embed.add_field(name="Price", value=f"${trade_data['price']:.4f}", inline=True)
           embed.add_field(name="Total", value=f"${trade_data['total']:.2f}", inline=True)
           embed.add_field(name="Strategy", value=trade_data['strategy'], inline=True)
           embed.add_field(name="Confidence", value=f"{trade_data['confidence']:.1f}%", inline=True)
           
           return embed
       
       @staticmethod
       def daily_report(report_data):
           """Template for daily performance reports"""
           color = 0x00ff00 if report_data['pnl'] >= 0 else 0xff0000
           
           embed = discord.Embed(
               title="📊 Daily Trading Report",
               color=color,
               timestamp=datetime.utcnow()
           )
           
           embed.add_field(name="P&L", value=f"${report_data['pnl']:.2f}", inline=True)
           embed.add_field(name="Trades", value=f"{report_data['total_trades']}", inline=True)
           embed.add_field(name="Win Rate", value=f"{report_data['win_rate']:.1f}%", inline=True)
           embed.add_field(name="Balance", value=f"${report_data['balance']:.2f}", inline=True)
           embed.add_field(name="Best Trade", value=f"${report_data['best_trade']:.2f}", inline=True)
           embed.add_field(name="Worst Trade", value=f"${report_data['worst_trade']:.2f}", inline=True)
           
           return embed
       
       @staticmethod
       def error_alert(error_data):
           """Template for error alerts"""
           embed = discord.Embed(
               title="⚠️ System Alert",
               description=error_data['message'],
               color=0xff0000,
               timestamp=datetime.utcnow()
           )
           
           embed.add_field(name="Error Type", value=error_data['type'], inline=True)
           embed.add_field(name="Severity", value=error_data['severity'], inline=True)
           embed.add_field(name="Component", value=error_data['component'], inline=True)
           
           return embed
   ```

## Step 7: Set Up Bot Commands

### Create Command Handler

1. **Create Commands File**
   ```bash
   nano src/discord_commands.py
   ```

2. **Add Command Functions**
   ```python
   import discord
   from discord.ext import commands
   
   class TradingBotCommands(commands.Cog):
       def __init__(self, bot, trading_bot):
           self.bot = bot
           self.trading_bot = trading_bot
       
       @commands.slash_command(name="status", description="Get bot status")
       async def status(self, ctx):
           """Get current bot status"""
           status_data = self.trading_bot.get_status()
           
           embed = discord.Embed(
               title="🤖 Bot Status",
               color=0x00ff00 if status_data['running'] else 0xff0000
           )
           
           embed.add_field(name="Status", value="🟢 Running" if status_data['running'] else "🔴 Stopped", inline=True)
           embed.add_field(name="Uptime", value=status_data['uptime'], inline=True)
           embed.add_field(name="Balance", value=f"${status_data['balance']:.2f}", inline=True)
           embed.add_field(name="Today's P&L", value=f"${status_data['daily_pnl']:.2f}", inline=True)
           embed.add_field(name="Active Positions", value=status_data['positions'], inline=True)
           embed.add_field(name="Last Trade", value=status_data['last_trade'], inline=True)
           
           await ctx.respond(embed=embed)
       
       @commands.slash_command(name="pause", description="Pause trading")
       async def pause(self, ctx):
           """Pause the trading bot"""
           self.trading_bot.pause()
           await ctx.respond("🛑 Trading paused")
       
       @commands.slash_command(name="resume", description="Resume trading")
       async def resume(self, ctx):
           """Resume the trading bot"""
           self.trading_bot.resume()
           await ctx.respond("▶️ Trading resumed")
       
       @commands.slash_command(name="report", description="Generate current report")
       async def report(self, ctx):
           """Generate and send current performance report"""
           await ctx.defer()  # This might take a moment
           
           report_path = self.trading_bot.generate_report()
           
           with open(report_path, 'rb') as f:
               file = discord.File(f, filename="trading_report.pdf")
               await ctx.followup.send("📈 Current Trading Report", file=file)
   ```

## Step 8: Configure Scheduled Reports

### Set Up Daily Report Scheduler

1. **Install Schedule Library**
   ```bash
   pip install schedule
   ```

2. **Create Scheduler**
   ```bash
   nano src/discord_scheduler.py
   ```

3. **Add Scheduling Logic**
   ```python
   import schedule
   import asyncio
   import threading
   from datetime import datetime
   
   class DiscordScheduler:
       def __init__(self, discord_client, trading_bot):
           self.discord_client = discord_client
           self.trading_bot = trading_bot
           
       def start_scheduler(self):
           """Start the scheduled tasks"""
           # Daily report at 9 AM UTC
           schedule.every().day.at("09:00").do(self.send_daily_report)
           
           # Hourly status check
           schedule.every().hour.do(self.hourly_check)
           
           # Run scheduler in separate thread
           scheduler_thread = threading.Thread(target=self.run_scheduler)
           scheduler_thread.daemon = True
           scheduler_thread.start()
       
       def run_scheduler(self):
           """Run the scheduler loop"""
           while True:
               schedule.run_pending()
               time.sleep(60)  # Check every minute
       
       async def send_daily_report(self):
           """Send daily performance report"""
           report_data = self.trading_bot.get_daily_stats()
           report_path = self.trading_bot.generate_pdf_report()
           
           channel = self.discord_client.get_channel(int(os.getenv('DISCORD_REPORTS_CHANNEL')))
           
           if channel:
               # Send summary embed
               embed = DiscordTemplates.daily_report(report_data)
               
               # Send PDF file
               with open(report_path, 'rb') as f:
                   file = discord.File(f, filename=f"report_{datetime.now().strftime('%Y%m%d')}.pdf")
                   await channel.send(embed=embed, file=file)
       
       async def hourly_check(self):
           """Hourly system health check"""
           if not self.trading_bot.is_healthy():
               channel = self.discord_client.get_channel(int(os.getenv('DISCORD_ALERTS_CHANNEL')))
               
               if channel:
                   embed = discord.Embed(
                       title="⚠️ System Health Warning",
                       description="Trading bot health check failed",
                       color=0xff9900
                   )
                   await channel.send(embed=embed)
   ```

## Troubleshooting

### Common Issues and Solutions

**Bot appears offline**
- Check bot token is correct
- Verify bot has proper permissions
- Ensure intents are enabled in Developer Portal

**Messages not sending**
- Verify channel IDs are correct
- Check bot has "Send Messages" permission in channels
- Ensure bot is in the server

**Slash commands not working**
- Re-invite bot with `applications.commands` scope
- Wait up to 1 hour for commands to sync globally
- Check bot has "Use Slash Commands" permission

**File uploads failing**
- Verify bot has "Attach Files" permission
- Check file size limits (8MB for regular servers, 50MB for boosted)
- Ensure file path exists and is readable

### Debug Commands

```bash
# Test bot connection
python -c "import discord; print(discord.__version__)"

# Check environment variables
env | grep DISCORD

# Test file permissions
ls -la ~/okx_trading_bot/reports/

# Monitor bot logs
tail -f logs/discord_bot.log
```

## Security Best Practices

1. **Token Security**
   - Never share bot token
   - Use environment variables
   - Regenerate token if compromised

2. **Server Security**
   - Limit bot permissions to minimum required
   - Use private server for trading notifications
   - Regular permission audits

3. **Command Security**
   - Restrict command usage to specific roles
   - Log all command executions
   - Implement rate limiting

## Next Steps

After completing Discord integration:

1. ✅ Discord server created and configured
2. ✅ Bot application created with proper permissions
3. ✅ Notification templates configured
4. ✅ Commands and scheduling set up
5. ➡️ Continue to [OKX API Configuration](okx_api_config.md)
6. ➡️ Complete [Bot Installation](bot_installation.md)

---

**[Screenshot: Discord Developer Portal showing bot application with token section]**

**[Screenshot: Discord server with organized channels for trading notifications]**

**[Screenshot: Example trade notification embed in Discord channel]**

**[Screenshot: Daily report PDF attachment in Discord reports channel]**
