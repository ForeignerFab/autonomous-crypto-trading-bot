
# OKX Autonomous Trading Bot

A comprehensive high-frequency cryptocurrency trading bot for OKX exchange with AI-enhanced decision making, Discord integration, and advanced risk management.

## 🚀 Features

### Core Trading Engine
- **High-Frequency Trading**: Optimized for 1-minute timeframes with rapid signal processing
- **Technical Analysis**: RSI, MACD, Bollinger Bands, EMA, VWAP, and volume indicators
- **Automatic Pair Selection**: Dynamic selection of profitable trading pairs based on volatility and momentum
- **Risk Management**: 2% risk per trade with position sizing and portfolio protection

### AI-Enhanced Decision Making
- **Ollama AI Integration**: Free, powerful AI using Ollama (llama3.2:7b or any model)
- **Pattern Recognition**: Detects bullish/bearish divergences, Bollinger squeezes, and volume patterns
- **Self-Learning**: Adapts parameters based on historical performance
- **Parameter Optimization**: AI-powered suggestions for RSI, MACD, and risk settings
- **Market Regime Detection**: Identifies trending vs. ranging market conditions
- **Intelligent Analysis**: AI-driven performance analysis and recommendations

### Discord Integration
- **Real-Time Notifications**: Trade executions, position updates, and error alerts
- **Interactive Commands**: Check status, balance, positions, and generate reports
- **Daily PDF Reports**: Comprehensive performance analysis delivered automatically
- **AI Suggestions**: Parameter optimization recommendations requiring user approval

### Risk Management System
- **Position Sizing**: Kelly Criterion and fixed-risk position sizing
- **Stop Loss/Take Profit**: Automatic exit orders with ATR-based levels
- **Portfolio Heat**: Maximum exposure limits and correlation risk management
- **Emergency Stops**: Circuit breakers for maximum drawdown protection

### Advanced Features
- **WSL Compatible**: Optimized for Windows Subsystem for Linux
- **24/7 Operation**: Robust error handling and automatic reconnection
- **Comprehensive Logging**: Detailed logs with performance metrics
- **Database Storage**: SQLite database for trade history and analytics
- **PDF Reporting**: Professional daily, weekly, and monthly reports

## 📋 Prerequisites

- Python 3.8 or higher
- OKX account with API access
- Discord account (optional, for notifications)
- Windows Subsystem for Linux (WSL) or Linux environment

## 🛠️ Installation

### 1. Clone and Setup

```bash
# Navigate to the bot directory
cd okx_trading_bot

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/WSL:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy configuration template
cp config_template.yml config.yml

# Copy environment template
cp .env.example .env
```

### 3. Configure API Keys

Edit `.env` file with your credentials:

```env
# OKX API Credentials (Required)
OKX_API_KEY=your_okx_api_key_here
OKX_SECRET_KEY=your_okx_secret_key_here
OKX_PASSPHRASE=your_okx_passphrase_here

# Discord Configuration (Optional)
DISCORD_BOT_TOKEN=your_discord_bot_token_here
DISCORD_CHANNEL_ID=your_discord_channel_id_here
DISCORD_WEBHOOK_URL=your_discord_webhook_url_here

# Security
ENCRYPTION_KEY=your_32_character_encryption_key_here
```

### 4. Configure Trading Parameters

Edit `config.yml` to customize your trading strategy:

```yaml
trading:
  initial_capital: 500.0      # Your starting capital
  risk_per_trade: 0.02        # 2% risk per trade
  max_risk_amount: 10.0       # Maximum £10 per trade
  max_active_pairs: 5         # Number of pairs to trade
  
  indicators:
    rsi:
      period: 5               # Fast RSI for HFT
      overbought: 80          # Tightened thresholds
      oversold: 20
    
    macd:
      fast_period: 6          # Optimized for HFT
      slow_period: 13
      signal_period: 5
```

## 🔑 OKX API Setup

1. **Create OKX Account**: Sign up at [OKX](https://www.okx.com)
2. **Enable API Access**:
   - Go to Account → API Management
   - Create new API key
   - Enable "Trade" permissions
   - Set IP restrictions for security
   - Note down API Key, Secret Key, and Passphrase

3. **Sandbox Testing** (Recommended):
   - Use OKX sandbox environment for testing
   - Set `sandbox: true` in config.yml
   - Get sandbox API credentials from OKX testnet

## 🤖 Discord Setup (Optional)

### Create Discord Bot

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create new application
3. Go to "Bot" section
4. Create bot and copy token
5. Enable necessary permissions:
   - Send Messages
   - Embed Links
   - Attach Files
   - Read Message History

### Setup Discord Server

1. Create Discord server or use existing
2. Create channel for bot notifications
3. Invite bot to server with permissions
4. Get channel ID (Enable Developer Mode → Right-click channel → Copy ID)

### Webhook Setup (Alternative)

1. Go to channel settings → Integrations → Webhooks
2. Create new webhook
3. Copy webhook URL

## 🚀 Running the Bot

### Prerequisites

**Ollama AI Setup (Optional but Recommended):**
```bash
# Install Ollama (if using locally)
# Windows: Download from https://ollama.ai
# Linux/WSL:
curl -fsSL https://ollama.ai/install.sh | sh

# Pull model
ollama pull llama3.2:7b

# Start Ollama service
ollama serve
```

**Or use external Ollama service** - Set `OLLAMA_BASE_URL` in config.yml

### Development Mode

```bash
# Activate virtual environment
source venv/bin/activate  # Linux/WSL
# or
venv\Scripts\activate     # Windows

# Run the bot
python main.py
```

### Cloud Deployment

See `../CLOUD_DEPLOYMENT_GUIDE.md` for detailed cloud hosting instructions.

**Quick Deploy Options:**
- **Railway.app** (Recommended) - Easy setup, $5/month for 24/7
- **Render.com** - Free tier available
- **Fly.io** - Good free tier
- **Oracle Cloud** - Always free VMs

### Production Mode (24/7)

```bash
# Make run script executable
chmod +x run_bot.sh

# Run in background with nohup
nohup ./run_bot.sh &

# Check if running
ps aux | grep python

# View logs
tail -f logs/trading_bot.log
```

### WSL Specific Setup

```bash
# Ensure WSL has access to Windows filesystem
cd /mnt/c/your/bot/directory

# Install additional dependencies if needed
sudo apt update
sudo apt install python3-pip python3-venv

# Follow standard installation steps
```

## 📊 Monitoring and Control

### Discord Commands

- `!status` - Get bot status and uptime
- `!balance` - Check account balance
- `!positions` - View open positions
- `!report` - Generate trading report
- `!stop` - Emergency stop (closes all positions)

### Log Files

- `logs/trading_bot.log` - General application logs
- `logs/errors.log` - Error-specific logs
- `reports/` - Generated PDF reports
- `data/trading_bot.db` - SQLite database

### Performance Monitoring

The bot includes built-in performance monitoring:

- Real-time P&L tracking
- Win rate and profit factor calculation
- Drawdown monitoring
- Risk metrics analysis

## ⚙️ Advanced Configuration

### Technical Indicators

Customize indicator parameters in `config.yml`:

```yaml
indicators:
  rsi:
    period: 5               # 3-12 for HFT
    overbought: 80          # 70-90
    oversold: 20            # 10-30
  
  bollinger_bands:
    period: 12              # 10-20
    std_dev: 1.5            # 1.0-2.5
```

### Risk Management

```yaml
risk_management:
  max_daily_loss: 50.0      # Maximum daily loss
  max_drawdown: 100.0       # Maximum total drawdown
  position_sizing_method: "fixed_risk"  # fixed_risk, kelly
  correlation_limit: 0.7    # Maximum correlation between positions
```

### AI Assistant

```yaml
ai_assistant:
  enabled: true
  learning_rate: 0.01
  min_confidence: 0.7       # Minimum confidence for suggestions
  lookback_period: 30       # Days of data for learning
```

## 🔧 Troubleshooting

### Common Issues

1. **API Connection Errors**
   - Verify API credentials in `.env`
   - Check IP restrictions on OKX
   - Ensure API permissions are enabled

2. **Discord Bot Not Responding**
   - Verify bot token and permissions
   - Check channel ID is correct
   - Ensure bot is invited to server

3. **Database Errors**
   - Check file permissions in `data/` directory
   - Ensure SQLite is installed
   - Verify disk space availability

4. **WSL Issues**
   - Update WSL to version 2
   - Install required Python packages
   - Check file path permissions

### Performance Optimization

1. **Reduce Latency**
   - Use VPS near OKX servers
   - Optimize network settings
   - Use SSD storage

2. **Memory Usage**
   - Limit historical data retention
   - Optimize indicator calculations
   - Regular database cleanup

## 📈 Strategy Optimization

### Backtesting

The bot includes basic backtesting capabilities:

```python
# Run backtest on historical data
python -m src.backtest --symbol BTC-USDT --days 30
```

### Parameter Tuning

1. **RSI Period**: 3-12 (lower = more sensitive)
2. **MACD Fast**: 5-12 (faster = more signals)
3. **Bollinger Std Dev**: 1.0-2.5 (lower = more signals)
4. **Risk per Trade**: 1-3% (higher = more aggressive)

### Market Conditions

- **Trending Markets**: Use momentum indicators (MACD, EMA)
- **Ranging Markets**: Use mean reversion (RSI, Bollinger Bands)
- **High Volatility**: Reduce position sizes
- **Low Volatility**: Wait for breakouts

## 🛡️ Security Best Practices

1. **API Security**
   - Use read-only keys for testing
   - Set IP restrictions
   - Regularly rotate keys
   - Never share credentials

2. **Environment Security**
   - Use strong encryption keys
   - Secure .env file permissions
   - Regular security updates
   - Monitor for unauthorized access

3. **Risk Management**
   - Start with small capital
   - Use sandbox mode first
   - Set strict stop losses
   - Monitor positions regularly

## 📚 Additional Resources

### Documentation
- [OKX API Documentation](https://www.okx.com/docs-v5/en/)
- [Discord.py Documentation](https://discordpy.readthedocs.io/)
- [TA-Lib Documentation](https://ta-lib.org/)

### Support
- Check logs for error details
- Review configuration settings
- Test with sandbox mode first
- Monitor Discord notifications

### Updates
- Regularly update dependencies
- Monitor bot performance
- Review and adjust parameters
- Backup configuration and data

## ⚠️ Disclaimer

This trading bot is for educational and research purposes. Cryptocurrency trading involves significant risk and can result in financial loss. Always:

- Start with small amounts
- Use sandbox/demo mode first
- Understand the risks involved
- Never invest more than you can afford to lose
- Monitor the bot's performance regularly
- Have proper risk management in place

The developers are not responsible for any financial losses incurred through the use of this software.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
