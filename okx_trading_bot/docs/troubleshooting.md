
# Troubleshooting Guide

This comprehensive troubleshooting guide helps you diagnose and resolve common issues with your autonomous cryptocurrency trading bot. Issues are organized by category with step-by-step solutions.

## Quick Diagnostic Commands

Before diving into specific issues, run these diagnostic commands:

```bash
# Check bot status
./status.sh

# Check system resources
free -h && df -h

# Check recent logs
tail -20 logs/trading_bot.log

# Test API connections
python validate_okx.py
python test_discord.py

# Check environment variables
env | grep -E "(OKX|DISCORD)" | head -10
```

## WSL and Environment Issues

### WSL Won't Start or Crashes

**Symptoms:**
- WSL fails to start
- Ubuntu crashes on launch
- "The Windows Subsystem for Linux instance has terminated"

**Solutions:**

1. **Restart WSL Service**
   ```powershell
   # In Windows PowerShell (Admin)
   wsl --shutdown
   wsl --unregister Ubuntu
   wsl --install -d Ubuntu
   ```

2. **Check Virtualization**
   ```powershell
   # Verify virtualization is enabled
   systeminfo | findstr /i "Hyper-V"
   ```
   - If not enabled, enable in BIOS/UEFI settings
   - Enable Hyper-V in Windows Features

3. **Update WSL Kernel**
   ```powershell
   wsl --update
   wsl --shutdown
   ```

4. **Reset Network Configuration**
   ```bash
   # Inside WSL
   sudo rm /etc/resolv.conf
   sudo bash -c 'echo "nameserver 8.8.8.8" > /etc/resolv.conf'
   ```

### Python Environment Issues

**Symptoms:**
- "python: command not found"
- "No module named 'okx'"
- Virtual environment not activating

**Solutions:**

1. **Reinstall Python and Dependencies**
   ```bash
   sudo apt update
   sudo apt install -y python3 python3-pip python3-venv
   ```

2. **Recreate Virtual Environment**
   ```bash
   cd ~/okx_trading_bot
   rm -rf venv
   python3 -m venv venv
   source venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **Fix Python Path Issues**
   ```bash
   # Add to ~/.bashrc
   echo 'export PATH="/usr/bin/python3:$PATH"' >> ~/.bashrc
   echo 'alias python=python3' >> ~/.bashrc
   source ~/.bashrc
   ```

### File Permission Issues

**Symptoms:**
- "Permission denied" errors
- Cannot write to logs or data directories
- Scripts won't execute

**Solutions:**

1. **Fix Directory Permissions**
   ```bash
   cd ~/okx_trading_bot
   chmod 755 data logs reports backups temp
   chmod 600 .env
   chmod +x *.sh
   ```

2. **Fix Ownership Issues**
   ```bash
   sudo chown -R $USER:$USER ~/okx_trading_bot
   ```

3. **Check Disk Space**
   ```bash
   df -h
   # If disk full, clean up:
   find logs/ -name "*.log.*" -mtime +7 -delete
   ```

## API Connection Issues

### OKX API Problems

**Symptoms:**
- "Invalid signature" errors
- "API key not found"
- "Too many requests"
- Connection timeouts

**Solutions:**

1. **Verify API Credentials**
   ```bash
   # Check environment variables
   echo $OKX_API_KEY | head -c 20
   echo $OKX_SECRET_KEY | head -c 20
   echo $OKX_PASSPHRASE
   ```

2. **Test API Connection**
   ```bash
   python validate_okx.py
   ```

3. **Fix Signature Issues**
   ```bash
   # Sync system time (critical for API signatures)
   sudo ntpdate -s time.nist.gov
   
   # Or install NTP
   sudo apt install ntp
   sudo systemctl start ntp
   ```

4. **Handle Rate Limiting**
   ```python
   # In your code, implement proper rate limiting
   import time
   
   def rate_limited_request():
       time.sleep(0.1)  # 100ms between requests
       # Make API request
   ```

5. **Check IP Whitelist**
   - Verify your current IP: `curl ifconfig.me`
   - Update IP whitelist in OKX API settings
   - Consider using VPS with static IP

6. **API Permission Issues**
   ```bash
   # Verify API permissions in OKX dashboard
   # Ensure "Trade" permission is enabled
   # Disable "Withdraw" and "Funding" for security
   ```

### Discord API Problems

**Symptoms:**
- Bot appears offline
- Messages not sending
- "Forbidden" errors
- Slash commands not working

**Solutions:**

1. **Verify Bot Token**
   ```bash
   # Test token format (should be long string with dots)
   echo $DISCORD_BOT_TOKEN | wc -c
   # Should be 70+ characters
   ```

2. **Check Bot Permissions**
   - Verify bot has "Send Messages" permission
   - Check "Embed Links" and "Attach Files" permissions
   - Ensure bot is in the server

3. **Re-invite Bot with Correct Permissions**
   ```
   https://discord.com/api/oauth2/authorize?client_id=YOUR_BOT_ID&permissions=2147483647&scope=bot%20applications.commands
   ```

4. **Test Discord Connection**
   ```bash
   python test_discord.py
   ```

5. **Fix Channel ID Issues**
   ```bash
   # Verify channel IDs are correct
   echo $DISCORD_TRADES_CHANNEL
   # Should be 18-19 digit number
   ```

## Trading Bot Issues

### Bot Won't Start

**Symptoms:**
- Bot exits immediately
- "Configuration error" messages
- Import errors

**Solutions:**

1. **Run System Test**
   ```bash
   python test_system.py
   ```

2. **Check Configuration**
   ```bash
   # Verify .env file exists and has correct format
   cat .env | head -10
   
   # Check for missing variables
   python -c "
   import os
   from dotenv import load_dotenv
   load_dotenv()
   required = ['OKX_API_KEY', 'DISCORD_BOT_TOKEN']
   missing = [var for var in required if not os.getenv(var)]
   print('Missing:', missing)
   "
   ```

3. **Check Database**
   ```bash
   # Verify database exists and is accessible
   ls -la data/trading_bot.db
   
   # Reinitialize if corrupted
   rm data/trading_bot.db
   python scripts/init_database.py
   ```

4. **Check Dependencies**
   ```bash
   pip list | grep -E "(okx|discord|pandas)"
   
   # Reinstall if missing
   pip install -r requirements.txt
   ```

### Bot Stops Trading

**Symptoms:**
- Bot running but no trades
- "No trading opportunities" messages
- Risk limits reached

**Solutions:**

1. **Check Risk Limits**
   ```bash
   # Check daily loss limit
   python -c "
   import sqlite3
   from datetime import date
   conn = sqlite3.connect('data/trading_bot.db')
   cursor = conn.cursor()
   cursor.execute('SELECT pnl FROM performance WHERE date = ?', (date.today(),))
   result = cursor.fetchone()
   print('Today PnL:', result[0] if result else 0)
   conn.close()
   "
   ```

2. **Check Market Conditions**
   ```bash
   # Test market data access
   python -c "
   from src.okx_client import OKXClient
   client = OKXClient()
   ticker = client.get_ticker('BTC-USDT')
   print('BTC Price:', ticker.get('price', 'Error'))
   "
   ```

3. **Adjust Trading Parameters**
   ```bash
   # Lower confidence threshold temporarily
   nano .env
   # Change CONFIDENCE_THRESHOLD from 0.7 to 0.6
   ```

4. **Check Signal Generation**
   ```bash
   # Monitor signal generation
   tail -f logs/trading_bot.log | grep -i signal
   ```

### Incorrect Trade Execution

**Symptoms:**
- Wrong position sizes
- Unexpected buy/sell orders
- Stop losses not working

**Solutions:**

1. **Verify Position Sizing**
   ```python
   # Check position size calculation
   def debug_position_size():
       balance = 500.0  # Your balance
       risk_per_trade = 0.02  # 2%
       stop_loss_pct = 0.02  # 2%
       
       risk_amount = balance * risk_per_trade
       position_size = risk_amount / stop_loss_pct
       
       print(f"Risk amount: £{risk_amount}")
       print(f"Position size: £{position_size}")
   
   debug_position_size()
   ```

2. **Check Order Parameters**
   ```bash
   # Review recent trades
   tail -20 logs/trades.log
   ```

3. **Verify Stop Loss Logic**
   ```python
   # Test stop loss calculation
   entry_price = 43000  # Example BTC price
   stop_loss_pct = 0.02
   stop_price = entry_price * (1 - stop_loss_pct)
   print(f"Entry: ${entry_price}, Stop: ${stop_price}")
   ```

## Performance Issues

### High CPU/Memory Usage

**Symptoms:**
- System becomes slow
- Bot consumes excessive resources
- WSL becomes unresponsive

**Solutions:**

1. **Monitor Resource Usage**
   ```bash
   # Check current usage
   htop
   
   # Check bot processes
   ps aux | grep python
   ```

2. **Optimize WSL Resources**
   ```powershell
   # Create/edit .wslconfig in Windows user directory
   [wsl2]
   memory=2GB
   processors=2
   swap=1GB
   ```

3. **Reduce Update Frequency**
   ```bash
   # In .env file, increase update intervals
   UPDATE_INTERVAL=120  # 2 minutes instead of 1
   HEALTH_CHECK_INTERVAL=600  # 10 minutes instead of 5
   ```

4. **Clean Up Logs**
   ```bash
   # Remove old log files
   find logs/ -name "*.log.*" -mtime +3 -delete
   
   # Compress current logs
   gzip logs/*.log
   ```

### Slow API Responses

**Symptoms:**
- Delayed trade execution
- Timeout errors
- Missed trading opportunities

**Solutions:**

1. **Test Network Speed**
   ```bash
   # Test connection to OKX
   ping www.okx.com
   
   # Test DNS resolution
   nslookup www.okx.com
   ```

2. **Optimize API Calls**
   ```python
   # Implement connection pooling
   import requests
   
   session = requests.Session()
   # Use session for all API calls
   ```

3. **Reduce API Call Frequency**
   ```bash
   # In configuration, reduce polling frequency
   API_POLL_INTERVAL=30  # 30 seconds instead of 10
   ```

4. **Use WebSocket for Real-time Data**
   ```python
   # Consider implementing WebSocket for price feeds
   # This reduces API calls significantly
   ```

## Database Issues

### Database Corruption

**Symptoms:**
- "Database is locked" errors
- Corrupted data
- Cannot read/write to database

**Solutions:**

1. **Check Database Integrity**
   ```bash
   sqlite3 data/trading_bot.db "PRAGMA integrity_check;"
   ```

2. **Backup and Restore**
   ```bash
   # Create backup
   cp data/trading_bot.db backups/trading_bot_backup_$(date +%Y%m%d).db
   
   # Restore from backup if needed
   cp backups/trading_bot_backup_YYYYMMDD.db data/trading_bot.db
   ```

3. **Rebuild Database**
   ```bash
   # If corruption is severe
   rm data/trading_bot.db
   python scripts/init_database.py
   ```

4. **Fix Permissions**
   ```bash
   chmod 644 data/trading_bot.db
   chown $USER:$USER data/trading_bot.db
   ```

### Missing Data

**Symptoms:**
- No trading history
- Missing performance data
- Empty reports

**Solutions:**

1. **Check Data Insertion**
   ```bash
   sqlite3 data/trading_bot.db "SELECT COUNT(*) FROM trades;"
   sqlite3 data/trading_bot.db "SELECT COUNT(*) FROM market_data;"
   ```

2. **Verify Logging**
   ```bash
   # Check if data is being logged
   tail -f logs/trading_bot.log | grep -i "database\|insert\|trade"
   ```

3. **Manual Data Recovery**
   ```python
   # Script to recover data from logs
   import re
   import sqlite3
   
   def recover_trades_from_logs():
       with open('logs/trades.log', 'r') as f:
           # Parse log entries and insert into database
           pass
   ```

## Discord Integration Issues

### Messages Not Sending

**Symptoms:**
- No Discord notifications
- Bot appears online but silent
- Error messages in logs

**Solutions:**

1. **Check Channel Permissions**
   ```bash
   # Verify bot can send messages to channels
   python -c "
   import discord
   import asyncio
   import os
   
   async def test_channels():
       client = discord.Client(intents=discord.Intents.default())
       await client.login(os.getenv('DISCORD_BOT_TOKEN'))
       
       channel = client.get_channel(int(os.getenv('DISCORD_TRADES_CHANNEL')))
       if channel:
           print(f'Channel found: {channel.name}')
           perms = channel.permissions_for(channel.guild.me)
           print(f'Can send messages: {perms.send_messages}')
       
       await client.close()
   
   asyncio.run(test_channels())
   "
   ```

2. **Test Message Sending**
   ```bash
   python test_discord.py
   ```

3. **Check Message Limits**
   ```python
   # Ensure messages aren't too long
   def truncate_message(message, max_length=2000):
       if len(message) > max_length:
           return message[:max_length-3] + "..."
       return message
   ```

### File Upload Issues

**Symptoms:**
- PDF reports not uploading
- "File too large" errors
- Upload timeouts

**Solutions:**

1. **Check File Size**
   ```bash
   ls -lh reports/*.pdf
   # Discord limit: 8MB for regular servers, 50MB for boosted
   ```

2. **Compress PDF Files**
   ```python
   # Use compression when generating PDFs
   from reportlab.lib.pagesizes import letter
   from reportlab.platypus import SimpleDocTemplate
   
   doc = SimpleDocTemplate(
       filename,
       pagesize=letter,
       compress=1  # Enable compression
   )
   ```

3. **Split Large Reports**
   ```python
   def split_large_report(report_data):
       if len(report_data) > 1000:  # Split if too large
           return [report_data[:500], report_data[500:]]
       return [report_data]
   ```

## Network and Connectivity Issues

### Internet Connection Problems

**Symptoms:**
- "Connection refused" errors
- Intermittent API failures
- DNS resolution failures

**Solutions:**

1. **Test Basic Connectivity**
   ```bash
   # Test internet connection
   ping 8.8.8.8
   
   # Test DNS
   nslookup google.com
   
   # Test HTTPS
   curl -I https://www.okx.com
   ```

2. **Configure DNS**
   ```bash
   # Use reliable DNS servers
   sudo bash -c 'echo "nameserver 8.8.8.8" > /etc/resolv.conf'
   sudo bash -c 'echo "nameserver 1.1.1.1" >> /etc/resolv.conf'
   ```

3. **Check Firewall**
   ```bash
   # Check if firewall is blocking connections
   sudo ufw status
   
   # Allow outbound HTTPS if needed
   sudo ufw allow out 443
   ```

### VPN/Proxy Issues

**Symptoms:**
- API calls blocked by region
- Inconsistent connection
- IP-based restrictions

**Solutions:**

1. **Check Current IP**
   ```bash
   curl ifconfig.me
   ```

2. **Update IP Whitelist**
   - Log into OKX account
   - Update API key IP whitelist
   - Add new IP address

3. **Configure Proxy (if needed)**
   ```bash
   # Set proxy environment variables
   export https_proxy=http://proxy:port
   export http_proxy=http://proxy:port
   ```

## Logging and Monitoring Issues

### Log Files Not Created

**Symptoms:**
- Empty logs directory
- No log output
- Cannot track bot activity

**Solutions:**

1. **Check Log Directory Permissions**
   ```bash
   ls -la logs/
   chmod 755 logs/
   ```

2. **Test Logging Configuration**
   ```bash
   python config/logging_config.py
   ```

3. **Manual Log Creation**
   ```bash
   touch logs/trading_bot.log
   chmod 644 logs/trading_bot.log
   ```

### Log Files Too Large

**Symptoms:**
- Disk space running out
- Slow log access
- System performance issues

**Solutions:**

1. **Implement Log Rotation**
   ```python
   import logging.handlers
   
   handler = logging.handlers.RotatingFileHandler(
       'logs/trading_bot.log',
       maxBytes=10*1024*1024,  # 10MB
       backupCount=5
   )
   ```

2. **Clean Old Logs**
   ```bash
   # Remove logs older than 7 days
   find logs/ -name "*.log.*" -mtime +7 -delete
   
   # Compress current logs
   gzip logs/*.log
   ```

3. **Reduce Log Verbosity**
   ```bash
   # In .env file
   LOG_LEVEL=WARNING  # Instead of INFO or DEBUG
   ```

## Emergency Procedures

### Bot Malfunction - Immediate Stop

```bash
# Emergency stop procedure
pkill -f "python main.py"
pkill -f "okx_trading_bot"

# Check for any remaining positions
python -c "
from src.okx_client import OKXClient
client = OKXClient()
positions = client.get_positions()
print('Active positions:', len(positions))
for pos in positions:
    print(f'{pos[\"instId\"]}: {pos[\"pos\"]}')
"

# Close all positions if needed (EMERGENCY ONLY)
# python emergency_close_positions.py
```

### Data Recovery

```bash
# Backup current state
mkdir -p emergency_backup/$(date +%Y%m%d_%H%M%S)
cp -r data/ logs/ reports/ emergency_backup/$(date +%Y%m%d_%H%M%S)/

# Restore from backup
# cp -r emergency_backup/YYYYMMDD_HHMMSS/* ./
```

### System Reset

```bash
# Complete system reset (LAST RESORT)
./stop_bot.sh
rm -rf data/trading_bot.db
rm -rf logs/*.log
python scripts/init_database.py
python test_system.py
```

## Getting Help

### Diagnostic Information to Collect

When seeking help, collect this information:

```bash
# System information
uname -a
python --version
pip list | grep -E "(okx|discord|pandas)"

# Configuration (sanitized)
env | grep -E "(OKX|DISCORD)" | sed 's/=.*/=***HIDDEN***/'

# Recent logs
tail -50 logs/trading_bot.log > debug_logs.txt

# Error messages
grep -i error logs/*.log | tail -20

# System resources
free -h
df -h
```

### Log Analysis

```bash
# Find common errors
grep -i "error\|exception\|failed" logs/trading_bot.log | sort | uniq -c

# Check API call patterns
grep -i "api" logs/trading_bot.log | tail -20

# Monitor real-time issues
tail -f logs/trading_bot.log | grep -i "error\|warning"
```

## Prevention Tips

### Regular Maintenance

1. **Daily Checks**
   ```bash
   ./status.sh
   tail -10 logs/trading_bot.log
   ```

2. **Weekly Maintenance**
   ```bash
   # Update dependencies
   pip install --upgrade -r requirements.txt
   
   # Clean logs
   find logs/ -name "*.log.*" -mtime +7 -delete
   
   # Backup database
   cp data/trading_bot.db backups/weekly_backup_$(date +%Y%m%d).db
   ```

3. **Monthly Reviews**
   - Review trading performance
   - Update API keys if needed
   - Check system resource usage
   - Update bot configuration

### Monitoring Setup

```bash
# Create monitoring script
nano monitor_bot.sh

#!/bin/bash
# Check if bot is running
if ! pgrep -f "python main.py" > /dev/null; then
    echo "Bot not running - restarting"
    cd ~/okx_trading_bot
    ./start_bot.sh &
fi

# Add to crontab for automatic monitoring
crontab -e
# Add: */5 * * * * /home/ubuntu/okx_trading_bot/monitor_bot.sh
```

---

**[Screenshot: System diagnostic output showing all tests passing]**

**[Screenshot: Log file analysis showing common error patterns]**

**[Screenshot: Resource monitoring dashboard with CPU and memory usage]**

**[Screenshot: Emergency stop procedure successfully executed]**
