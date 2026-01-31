
# Bot Installation & Configuration Guide

This comprehensive guide walks you through the complete installation and configuration of your autonomous cryptocurrency trading bot, from initial setup to running your first trades.

## Prerequisites

Before starting, ensure you have completed:
- ✅ [WSL Setup](wsl_setup.md) - Ubuntu environment configured
- ✅ [Discord Integration](discord_integration.md) - Bot and notifications ready
- ✅ [OKX API Configuration](okx_api_config.md) - Trading API access configured

## Step 1: Download and Setup Bot Files

### Clone or Download Bot Code

1. **Navigate to Home Directory**
   ```bash
   cd ~
   ```

2. **Verify Bot Directory Exists**
   ```bash
   ls -la okx_trading_bot/
   ```

3. **Check Directory Structure**
   Your bot directory should contain:
   ```
   okx_trading_bot/
   ├── main.py                 # Main bot entry point
   ├── requirements.txt        # Python dependencies
   ├── config/                 # Configuration files
   │   ├── __init__.py
   │   ├── settings.py
   │   ├── discord_config.py
   │   └── okx_config.py
   ├── src/                    # Source code
   │   ├── __init__.py
   │   ├── trading_engine.py
   │   ├── strategy/
   │   ├── risk_management.py
   │   ├── okx_client.py
   │   ├── discord_client.py
   │   └── utils/
   ├── data/                   # Market data storage
   ├── logs/                   # Log files
   ├── reports/                # Generated reports
   ├── docs/                   # Documentation
   └── tests/                  # Test files
   ```

## Step 2: Create Python Virtual Environment

### Set Up Isolated Environment

1. **Create Virtual Environment**
   ```bash
   cd ~/okx_trading_bot
   python3 -m venv venv
   ```

2. **Activate Virtual Environment**
   ```bash
   source venv/bin/activate
   ```

3. **Upgrade pip**
   ```bash
   pip install --upgrade pip
   ```

4. **Verify Virtual Environment**
   ```bash
   which python
   # Should show: /home/ubuntu/okx_trading_bot/venv/bin/python
   ```

### Install Dependencies

1. **Install Required Packages**
   ```bash
   pip install -r requirements.txt
   ```

2. **Verify Installation**
   ```bash
   pip list
   ```

   Expected packages:
   ```
   discord.py>=2.3.0
   okx>=1.0.0
   pandas>=2.0.0
   numpy>=1.24.0
   requests>=2.31.0
   python-dotenv>=1.0.0
   schedule>=1.2.0
   matplotlib>=3.7.0
   seaborn>=0.12.0
   plotly>=5.15.0
   reportlab>=4.0.0
   ta>=0.10.0
   scikit-learn>=1.3.0
   ```

3. **Install Additional Dependencies**
   ```bash
   # For PDF generation
   pip install weasyprint

   # For advanced charting
   pip install mplfinance

   # For database support
   pip install sqlite3
   ```

## Step 3: Configure Environment Variables

### Create Environment Configuration

1. **Create .env File**
   ```bash
   nano .env
   ```

2. **Add Complete Configuration**
   ```bash
   # Trading Bot Configuration
   BOT_NAME=OKX_Trading_Bot
   BOT_VERSION=1.0.0
   ENVIRONMENT=demo  # demo or live
   
   # Capital and Risk Management
   INITIAL_CAPITAL=500.00
   RISK_TOLERANCE=0.02  # 2% risk per trade
   MAX_DAILY_LOSS=10.00  # £10 max daily loss
   MAX_POSITIONS=3
   MIN_TRADE_SIZE=5.00
   
   # OKX API Configuration
   OKX_API_KEY=your_demo_api_key_here
   OKX_SECRET_KEY=your_demo_secret_key_here
   OKX_PASSPHRASE=your_demo_passphrase_here
   OKX_IS_DEMO=true
   OKX_BASE_URL=https://www.okx.com
   
   # Discord Configuration
   DISCORD_BOT_TOKEN=your_discord_bot_token_here
   DISCORD_GUILD_ID=your_server_id_here
   DISCORD_TRADES_CHANNEL=your_trades_channel_id
   DISCORD_ALERTS_CHANNEL=your_alerts_channel_id
   DISCORD_REPORTS_CHANNEL=your_reports_channel_id
   DISCORD_COMMANDS_CHANNEL=your_commands_channel_id
   DISCORD_LOGS_CHANNEL=your_logs_channel_id
   
   # Trading Strategy Parameters
   STRATEGY_TYPE=traditional_ta  # traditional_ta or ml_enhanced
   TIMEFRAME=1m  # 1m, 5m, 15m, 1h
   RSI_PERIOD=14
   RSI_OVERSOLD=30
   RSI_OVERBOUGHT=70
   MA_FAST=12
   MA_SLOW=26
   MACD_SIGNAL=9
   BOLLINGER_PERIOD=20
   BOLLINGER_STD=2
   
   # AI Learning Parameters
   LEARNING_ENABLED=true
   LEARNING_RATE=0.001
   CONFIDENCE_THRESHOLD=0.7
   BACKTEST_DAYS=30
   
   # Operational Settings
   LOG_LEVEL=INFO
   LOG_RETENTION_DAYS=30
   REPORT_TIME=09:00  # UTC time for daily reports
   HEALTH_CHECK_INTERVAL=300  # 5 minutes
   
   # Database Configuration
   DATABASE_PATH=data/trading_bot.db
   BACKUP_INTERVAL=3600  # 1 hour
   
   # Security Settings
   API_RATE_LIMIT=10  # requests per second
   MAX_RETRIES=3
   TIMEOUT_SECONDS=30
   ```

3. **Secure Environment File**
   ```bash
   chmod 600 .env
   ```

## Step 4: Initialize Database and Directories

### Create Required Directories

1. **Create Directory Structure**
   ```bash
   mkdir -p data logs reports backups temp
   ```

2. **Set Proper Permissions**
   ```bash
   chmod 755 data logs reports backups temp
   ```

### Initialize Database

1. **Create Database Initialization Script**
   ```bash
   nano scripts/init_database.py
   ```

2. **Add Database Setup Code**
   ```python
   import sqlite3
   import os
   from datetime import datetime
   
   def initialize_database():
       """Initialize SQLite database with required tables"""
       db_path = "data/trading_bot.db"
       
       # Create database connection
       conn = sqlite3.connect(db_path)
       cursor = conn.cursor()
       
       # Create trades table
       cursor.execute('''
           CREATE TABLE IF NOT EXISTS trades (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
               symbol TEXT NOT NULL,
               side TEXT NOT NULL,
               size REAL NOT NULL,
               price REAL NOT NULL,
               total REAL NOT NULL,
               strategy TEXT NOT NULL,
               confidence REAL,
               pnl REAL DEFAULT 0,
               status TEXT DEFAULT 'open',
               order_id TEXT,
               created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
               updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
           )
       ''')
       
       # Create market_data table
       cursor.execute('''
           CREATE TABLE IF NOT EXISTS market_data (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
               symbol TEXT NOT NULL,
               price REAL NOT NULL,
               volume REAL,
               rsi REAL,
               macd REAL,
               signal REAL,
               bb_upper REAL,
               bb_lower REAL,
               created_at DATETIME DEFAULT CURRENT_TIMESTAMP
           )
       ''')
       
       # Create performance table
       cursor.execute('''
           CREATE TABLE IF NOT EXISTS performance (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               date DATE NOT NULL,
               starting_balance REAL NOT NULL,
               ending_balance REAL NOT NULL,
               pnl REAL NOT NULL,
               trades_count INTEGER DEFAULT 0,
               wins INTEGER DEFAULT 0,
               losses INTEGER DEFAULT 0,
               win_rate REAL DEFAULT 0,
               best_trade REAL DEFAULT 0,
               worst_trade REAL DEFAULT 0,
               created_at DATETIME DEFAULT CURRENT_TIMESTAMP
           )
       ''')
       
       # Create settings table
       cursor.execute('''
           CREATE TABLE IF NOT EXISTS settings (
               key TEXT PRIMARY KEY,
               value TEXT NOT NULL,
               updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
           )
       ''')
       
       # Insert initial settings
       initial_settings = [
           ('bot_version', '1.0.0'),
           ('initial_capital', '500.00'),
           ('risk_tolerance', '0.02'),
           ('strategy_type', 'traditional_ta'),
           ('learning_enabled', 'true'),
           ('last_backup', datetime.now().isoformat())
       ]
       
       cursor.executemany(
           'INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)',
           initial_settings
       )
       
       # Commit changes and close
       conn.commit()
       conn.close()
       
       print("✅ Database initialized successfully")
       print(f"   Database location: {os.path.abspath(db_path)}")
   
   if __name__ == "__main__":
       initialize_database()
   ```

3. **Run Database Initialization**
   ```bash
   python scripts/init_database.py
   ```

## Step 5: Configure Logging System

### Create Logging Configuration

1. **Create Logging Config**
   ```bash
   nano config/logging_config.py
   ```

2. **Add Logging Setup**
   ```python
   import logging
   import logging.handlers
   import os
   from datetime import datetime
   
   def setup_logging():
       """Configure comprehensive logging system"""
       
       # Create logs directory if it doesn't exist
       os.makedirs('logs', exist_ok=True)
       
       # Configure root logger
       logging.basicConfig(
           level=logging.INFO,
           format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
           handlers=[
               # Console handler
               logging.StreamHandler(),
               
               # Main log file (rotating)
               logging.handlers.RotatingFileHandler(
                   'logs/trading_bot.log',
                   maxBytes=10*1024*1024,  # 10MB
                   backupCount=5
               ),
               
               # Error log file
               logging.handlers.RotatingFileHandler(
                   'logs/errors.log',
                   maxBytes=5*1024*1024,   # 5MB
                   backupCount=3
               )
           ]
       )
       
       # Create specialized loggers
       
       # Trading logger
       trading_logger = logging.getLogger('trading')
       trading_handler = logging.handlers.RotatingFileHandler(
           'logs/trades.log',
           maxBytes=10*1024*1024,
           backupCount=10
       )
       trading_handler.setFormatter(
           logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
       )
       trading_logger.addHandler(trading_handler)
       
       # Discord logger
       discord_logger = logging.getLogger('discord')
       discord_handler = logging.handlers.RotatingFileHandler(
           'logs/discord.log',
           maxBytes=5*1024*1024,
           backupCount=3
       )
       discord_handler.setFormatter(
           logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
       )
       discord_logger.addHandler(discord_handler)
       
       # API logger
       api_logger = logging.getLogger('api')
       api_handler = logging.handlers.RotatingFileHandler(
           'logs/api.log',
           maxBytes=5*1024*1024,
           backupCount=3
       )
       api_handler.setFormatter(
           logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
       )
       api_logger.addHandler(api_handler)
       
       print("✅ Logging system configured")
       print("   Log files:")
       print("   - logs/trading_bot.log (main)")
       print("   - logs/trades.log (trading)")
       print("   - logs/discord.log (notifications)")
       print("   - logs/api.log (API calls)")
       print("   - logs/errors.log (errors only)")
   
   if __name__ == "__main__":
       setup_logging()
   ```

3. **Initialize Logging**
   ```bash
   python config/logging_config.py
   ```

## Step 6: Test Individual Components

### Test OKX Connection

1. **Run OKX Test**
   ```bash
   python validate_okx.py
   ```

   Expected output:
   ```
   🔍 Validating OKX Configuration...
   ==================================================
   1. Testing account balance...
   ✅ Account balance retrieved
      Available USDT: 100000.0
   
   2. Testing market data...
   ✅ Market data retrieved
      BTC Price: $43250.5
   
   🎉 OKX configuration validated successfully!
   ```

### Test Discord Integration

1. **Run Discord Test**
   ```bash
   python test_discord.py
   ```

   Expected output:
   ```
   Bot connected as OKX-Trader#1234
   Test message sent successfully!
   ```

### Test Database Connection

1. **Create Database Test**
   ```bash
   nano test_database.py
   ```

2. **Add Test Code**
   ```python
   import sqlite3
   import os
   
   def test_database():
       """Test database connectivity and structure"""
       db_path = "data/trading_bot.db"
       
       if not os.path.exists(db_path):
           print("❌ Database not found. Run init_database.py first.")
           return False
       
       try:
           conn = sqlite3.connect(db_path)
           cursor = conn.cursor()
           
           # Test tables exist
           cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
           tables = [row[0] for row in cursor.fetchall()]
           
           expected_tables = ['trades', 'market_data', 'performance', 'settings']
           
           print("🔍 Testing database structure...")
           for table in expected_tables:
               if table in tables:
                   print(f"   ✅ Table '{table}' exists")
               else:
                   print(f"   ❌ Table '{table}' missing")
                   return False
           
           # Test insert/select
           cursor.execute("INSERT INTO settings (key, value) VALUES (?, ?)", 
                         ('test_key', 'test_value'))
           cursor.execute("SELECT value FROM settings WHERE key = ?", ('test_key',))
           result = cursor.fetchone()
           
           if result and result[0] == 'test_value':
               print("   ✅ Database read/write test passed")
               cursor.execute("DELETE FROM settings WHERE key = ?", ('test_key',))
           else:
               print("   ❌ Database read/write test failed")
               return False
           
           conn.commit()
           conn.close()
           
           print("🎉 Database test completed successfully!")
           return True
           
       except Exception as e:
           print(f"❌ Database test failed: {str(e)}")
           return False
   
   if __name__ == "__main__":
       test_database()
   ```

3. **Run Database Test**
   ```bash
   python test_database.py
   ```

## Step 7: Configure Trading Parameters

### Create Trading Configuration

1. **Edit Trading Settings**
   ```bash
   nano config/trading_config.py
   ```

2. **Add Trading Parameters**
   ```python
   import os
   from dataclasses import dataclass
   from typing import List, Dict
   
   @dataclass
   class TradingConfig:
       # Capital Management
       initial_capital: float = 500.0
       risk_per_trade: float = 0.02  # 2% risk per trade
       max_daily_loss: float = 10.0  # £10 max daily loss
       max_positions: int = 3
       min_trade_size: float = 5.0
       
       # Trading Pairs
       trading_pairs: List[str] = None
       primary_pair: str = "BTC-USDT"
       
       # Technical Analysis Parameters
       rsi_period: int = 14
       rsi_oversold: float = 30.0
       rsi_overbought: float = 70.0
       
       ma_fast: int = 12
       ma_slow: int = 26
       macd_signal: int = 9
       
       bollinger_period: int = 20
       bollinger_std: float = 2.0
       
       # Strategy Settings
       strategy_type: str = "traditional_ta"
       timeframe: str = "1m"  # 1m, 5m, 15m, 1h
       confidence_threshold: float = 0.7
       
       # Risk Management
       stop_loss_pct: float = 0.02  # 2% stop loss
       take_profit_pct: float = 0.04  # 4% take profit
       trailing_stop: bool = True
       trailing_stop_pct: float = 0.01  # 1% trailing stop
       
       # AI Learning
       learning_enabled: bool = True
       learning_rate: float = 0.001
       backtest_days: int = 30
       min_confidence: float = 0.6
       
       # Operational
       update_interval: int = 60  # seconds
       health_check_interval: int = 300  # 5 minutes
       max_api_retries: int = 3
       api_timeout: int = 30
       
       def __post_init__(self):
           if self.trading_pairs is None:
               self.trading_pairs = [
                   "BTC-USDT", "ETH-USDT", "ADA-USDT",
                   "DOT-USDT", "LINK-USDT", "SOL-USDT",
                   "MATIC-USDT", "AVAX-USDT", "ATOM-USDT"
               ]
           
           # Load from environment if available
           self.initial_capital = float(os.getenv('INITIAL_CAPITAL', self.initial_capital))
           self.risk_per_trade = float(os.getenv('RISK_TOLERANCE', self.risk_per_trade))
           self.max_daily_loss = float(os.getenv('MAX_DAILY_LOSS', self.max_daily_loss))
           self.strategy_type = os.getenv('STRATEGY_TYPE', self.strategy_type)
           self.timeframe = os.getenv('TIMEFRAME', self.timeframe)
           self.learning_enabled = os.getenv('LEARNING_ENABLED', 'true').lower() == 'true'
   
   # Global config instance
   trading_config = TradingConfig()
   ```

## Step 8: Run Initial System Test

### Create Comprehensive Test

1. **Create System Test Script**
   ```bash
   nano test_system.py
   ```

2. **Add System Test Code**
   ```python
   import sys
   import os
   import time
   from datetime import datetime
   
   # Add src to path
   sys.path.append('src')
   sys.path.append('config')
   
   from okx_client import OKXClient
   from discord_client import DiscordClient
   from trading_config import trading_config
   from logging_config import setup_logging
   
   def run_system_test():
       """Comprehensive system test"""
       print("🚀 Running Comprehensive System Test")
       print("=" * 60)
       
       # Setup logging
       setup_logging()
       
       test_results = {
           'environment': False,
           'database': False,
           'okx_api': False,
           'discord': False,
           'trading_config': False,
           'file_permissions': False
       }
       
       # Test 1: Environment Variables
       print("\n1. Testing Environment Configuration...")
       required_env_vars = [
           'OKX_API_KEY', 'OKX_SECRET_KEY', 'OKX_PASSPHRASE',
           'DISCORD_BOT_TOKEN', 'DISCORD_GUILD_ID'
       ]
       
       missing_vars = []
       for var in required_env_vars:
           if not os.getenv(var):
               missing_vars.append(var)
       
       if missing_vars:
           print(f"   ❌ Missing environment variables: {', '.join(missing_vars)}")
       else:
           print("   ✅ All required environment variables present")
           test_results['environment'] = True
       
       # Test 2: Database
       print("\n2. Testing Database...")
       try:
           import sqlite3
           conn = sqlite3.connect('data/trading_bot.db')
           cursor = conn.cursor()
           cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
           table_count = cursor.fetchone()[0]
           conn.close()
           
           if table_count >= 4:
               print(f"   ✅ Database initialized with {table_count} tables")
               test_results['database'] = True
           else:
               print(f"   ❌ Database incomplete: only {table_count} tables found")
       except Exception as e:
           print(f"   ❌ Database error: {str(e)}")
       
       # Test 3: OKX API
       print("\n3. Testing OKX API...")
       try:
           okx_client = OKXClient()
           balance = okx_client.get_account_balance()
           if balance['success']:
               print("   ✅ OKX API connection successful")
               test_results['okx_api'] = True
           else:
               print(f"   ❌ OKX API error: {balance['error']}")
       except Exception as e:
           print(f"   ❌ OKX API exception: {str(e)}")
       
       # Test 4: Discord (if token available)
       print("\n4. Testing Discord Integration...")
       if os.getenv('DISCORD_BOT_TOKEN'):
           try:
               # Simple token validation (don't actually connect)
               token = os.getenv('DISCORD_BOT_TOKEN')
               if len(token) > 50 and '.' in token:
                   print("   ✅ Discord token format valid")
                   test_results['discord'] = True
               else:
                   print("   ❌ Discord token format invalid")
           except Exception as e:
               print(f"   ❌ Discord test error: {str(e)}")
       else:
           print("   ⚠️ Discord token not configured")
       
       # Test 5: Trading Configuration
       print("\n5. Testing Trading Configuration...")
       try:
           config = trading_config
           if config.initial_capital > 0 and len(config.trading_pairs) > 0:
               print(f"   ✅ Trading config loaded: {len(config.trading_pairs)} pairs")
               print(f"   ✅ Initial capital: £{config.initial_capital}")
               print(f"   ✅ Risk per trade: {config.risk_per_trade*100}%")
               test_results['trading_config'] = True
           else:
               print("   ❌ Trading configuration invalid")
       except Exception as e:
           print(f"   ❌ Trading config error: {str(e)}")
       
       # Test 6: File Permissions
       print("\n6. Testing File Permissions...")
       test_dirs = ['data', 'logs', 'reports', 'backups']
       all_dirs_ok = True
       
       for dir_name in test_dirs:
           if os.path.exists(dir_name) and os.access(dir_name, os.W_OK):
               print(f"   ✅ {dir_name}/ directory writable")
           else:
               print(f"   ❌ {dir_name}/ directory not writable")
               all_dirs_ok = False
       
       test_results['file_permissions'] = all_dirs_ok
       
       # Summary
       print("\n" + "=" * 60)
       print("📊 SYSTEM TEST SUMMARY")
       print("=" * 60)
       
       passed_tests = sum(test_results.values())
       total_tests = len(test_results)
       
       for test_name, result in test_results.items():
           status = "✅ PASS" if result else "❌ FAIL"
           print(f"   {test_name.replace('_', ' ').title()}: {status}")
       
       print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
       
       if passed_tests == total_tests:
           print("\n🎉 All tests passed! Your trading bot is ready to run.")
           print("\nNext steps:")
           print("1. Run 'python main.py' to start the bot")
           print("2. Monitor logs in the logs/ directory")
           print("3. Check Discord for notifications")
           return True
       else:
           print(f"\n⚠️ {total_tests - passed_tests} tests failed. Please fix issues before running the bot.")
           return False
   
   if __name__ == "__main__":
       run_system_test()
   ```

3. **Run System Test**
   ```bash
   python test_system.py
   ```

## Step 9: Create Startup Scripts

### Create Bot Startup Script

1. **Create Startup Script**
   ```bash
   nano start_bot.sh
   ```

2. **Add Startup Logic**
   ```bash
   #!/bin/bash
   
   # OKX Trading Bot Startup Script
   echo "🚀 Starting OKX Trading Bot..."
   echo "================================"
   
   # Check if virtual environment exists
   if [ ! -d "venv" ]; then
       echo "❌ Virtual environment not found. Please run setup first."
       exit 1
   fi
   
   # Activate virtual environment
   source venv/bin/activate
   
   # Check if .env file exists
   if [ ! -f ".env" ]; then
       echo "❌ .env file not found. Please configure environment variables."
       exit 1
   fi
   
   # Create necessary directories
   mkdir -p logs data reports backups temp
   
   # Check Python dependencies
   echo "🔍 Checking dependencies..."
   python -c "import okx, discord, pandas, numpy" 2>/dev/null
   if [ $? -ne 0 ]; then
       echo "❌ Missing dependencies. Installing..."
       pip install -r requirements.txt
   fi
   
   # Run system test
   echo "🧪 Running system test..."
   python test_system.py --quiet
   if [ $? -ne 0 ]; then
       echo "❌ System test failed. Please check configuration."
       exit 1
   fi
   
   # Start the bot
   echo "▶️ Starting trading bot..."
   python main.py
   ```

3. **Make Script Executable**
   ```bash
   chmod +x start_bot.sh
   ```

### Create Stop Script

1. **Create Stop Script**
   ```bash
   nano stop_bot.sh
   ```

2. **Add Stop Logic**
   ```bash
   #!/bin/bash
   
   echo "🛑 Stopping OKX Trading Bot..."
   
   # Find and kill bot processes
   pkill -f "python main.py"
   pkill -f "okx_trading_bot"
   
   echo "✅ Trading bot stopped"
   
   # Show final status
   echo "📊 Final Status:"
   if [ -f "logs/trading_bot.log" ]; then
       echo "Last 5 log entries:"
       tail -5 logs/trading_bot.log
   fi
   ```

3. **Make Script Executable**
   ```bash
   chmod +x stop_bot.sh
   ```

### Create Status Check Script

1. **Create Status Script**
   ```bash
   nano status.sh
   ```

2. **Add Status Logic**
   ```bash
   #!/bin/bash
   
   echo "📊 OKX Trading Bot Status"
   echo "========================"
   
   # Check if bot is running
   if pgrep -f "python main.py" > /dev/null; then
       echo "Status: 🟢 RUNNING"
       echo "PID: $(pgrep -f 'python main.py')"
   else
       echo "Status: 🔴 STOPPED"
   fi
   
   # Show system resources
   echo ""
   echo "System Resources:"
   echo "Memory: $(free -h | grep '^Mem:' | awk '{print $3 "/" $2}')"
   echo "Disk: $(df -h . | tail -1 | awk '{print $3 "/" $2 " (" $5 " used)"}')"
   
   # Show recent logs
   if [ -f "logs/trading_bot.log" ]; then
       echo ""
       echo "Recent Activity (last 3 entries):"
       tail -3 logs/trading_bot.log
   fi
   
   # Show today's performance
   if [ -f "data/trading_bot.db" ]; then
       echo ""
       echo "Today's Performance:"
       python -c "
   import sqlite3
   from datetime import date
   
   conn = sqlite3.connect('data/trading_bot.db')
   cursor = conn.cursor()
   cursor.execute('SELECT * FROM performance WHERE date = ?', (date.today(),))
   result = cursor.fetchone()
   
   if result:
       print(f'P&L: £{result[3]:.2f}')
       print(f'Trades: {result[4]}')
       print(f'Win Rate: {result[7]:.1f}%')
   else:
       print('No trades today')
   
   conn.close()
   "
   fi
   ```

3. **Make Script Executable**
   ```bash
   chmod +x status.sh
   ```

## Step 10: First Bot Run

### Pre-Flight Checklist

Before running your bot for the first time:

- [ ] WSL environment configured
- [ ] Python virtual environment activated
- [ ] All dependencies installed
- [ ] Environment variables configured
- [ ] Database initialized
- [ ] OKX API tested (demo mode)
- [ ] Discord integration tested
- [ ] System test passed
- [ ] Startup scripts created

### Start the Bot

1. **Run Final System Test**
   ```bash
   python test_system.py
   ```

2. **Start Bot in Demo Mode**
   ```bash
   ./start_bot.sh
   ```

3. **Monitor Initial Startup**
   ```bash
   # In another terminal
   tail -f logs/trading_bot.log
   ```

### Expected Startup Output

```
🚀 Starting OKX Trading Bot...
================================
🔍 Checking dependencies...
🧪 Running system test...
📊 SYSTEM TEST SUMMARY
================================
   Environment: ✅ PASS
   Database: ✅ PASS
   Okx Api: ✅ PASS
   Discord: ✅ PASS
   Trading Config: ✅ PASS
   File Permissions: ✅ PASS

Overall: 6/6 tests passed
🎉 All tests passed! Your trading bot is ready to run.

▶️ Starting trading bot...

2025-01-27 10:00:00 - INFO - Trading bot starting up...
2025-01-27 10:00:01 - INFO - Environment: DEMO
2025-01-27 10:00:01 - INFO - Initial capital: £500.00
2025-01-27 10:00:02 - INFO - OKX API connected successfully
2025-01-27 10:00:03 - INFO - Discord bot connected
2025-01-27 10:00:04 - INFO - Database initialized
2025-01-27 10:00:05 - INFO - Trading engine started
2025-01-27 10:00:06 - INFO - Risk management active
2025-01-27 10:00:07 - INFO - Bot ready for trading
```

### Monitor First Hour

1. **Check Bot Status**
   ```bash
   ./status.sh
   ```

2. **Monitor Logs**
   ```bash
   # Main log
   tail -f logs/trading_bot.log
   
   # Trading activity
   tail -f logs/trades.log
   
   # Discord notifications
   tail -f logs/discord.log
   ```

3. **Check Discord Notifications**
   - Look for startup message in your Discord server
   - Verify channels are receiving notifications
   - Test bot commands if configured

## Troubleshooting Installation

### Common Issues

**Virtual Environment Issues**
```bash
# Recreate virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Permission Errors**
```bash
# Fix directory permissions
chmod 755 data logs reports backups temp
chmod 600 .env
chmod +x *.sh
```

**Database Errors**
```bash
# Reinitialize database
rm data/trading_bot.db
python scripts/init_database.py
```

**API Connection Issues**
```bash
# Test individual components
python validate_okx.py
python test_discord.py
```

**Missing Dependencies**
```bash
# Install missing packages
pip install --upgrade -r requirements.txt

# For specific issues
pip install --force-reinstall okx discord.py
```

### Debug Commands

```bash
# Check Python path
which python

# Check installed packages
pip list

# Check environment variables
env | grep -E "(OKX|DISCORD)"

# Check file permissions
ls -la

# Check running processes
ps aux | grep python

# Check system resources
free -h
df -h
```

## Next Steps

After successful installation:

1. ✅ Bot installed and configured
2. ✅ First successful startup completed
3. ✅ All systems tested and working
4. ➡️ Review [Trading Strategy](trading_strategy.md) to understand how it works
5. ➡️ Read [Best Practices](best_practices.md) for optimal operation
6. ➡️ Check [Troubleshooting Guide](troubleshooting.md) for common issues

## Maintenance Tasks

### Daily Tasks
- Check bot status: `./status.sh`
- Review logs for errors
- Monitor Discord notifications
- Check daily performance report

### Weekly Tasks
- Update dependencies: `pip install --upgrade -r requirements.txt`
- Clean old log files: `find logs/ -name "*.log.*" -mtime +7 -delete`
- Backup database: `cp data/trading_bot.db backups/`
- Review trading performance

### Monthly Tasks
- Update bot code if new version available
- Review and optimize trading parameters
- Analyze performance metrics
- Update API keys if needed

---

**[Screenshot: Successful system test showing all components passing]**

**[Screenshot: Bot startup logs showing successful initialization]**

**[Screenshot: Discord server receiving first bot notification]**

**[Screenshot: Status script output showing bot running and performance metrics]**
