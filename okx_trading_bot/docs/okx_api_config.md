
# OKX API Configuration Guide

This comprehensive guide walks you through setting up OKX API access for your autonomous trading bot, including account creation, API key generation, sandbox testing, and security configuration.

## Overview

Your trading bot requires OKX API access to:
- Execute buy/sell orders automatically
- Monitor account balance and positions
- Fetch real-time market data
- Manage risk and stop-losses
- Generate trading reports

## Step 1: Create OKX Account

### Main Account Setup

1. **Visit OKX Website**
   - Go to https://www.okx.com
   - Click "Sign Up" in the top-right corner

2. **Complete Registration**
   - Enter email address and create strong password
   - Verify email address via confirmation link
   - Complete phone number verification
   - Set up 2FA (Google Authenticator recommended)

3. **Complete KYC Verification**
   - Upload government-issued ID
   - Complete facial verification
   - Wait for approval (usually 24-48 hours)

### Demo Account Setup (Recommended for Testing)

1. **Access Demo Environment**
   - Visit https://www.okx.com/demo
   - Log in with your main account credentials
   - Demo account is automatically created

2. **Fund Demo Account**
   - Demo account comes with virtual funds
   - No real money at risk
   - Perfect for testing your bot

## Step 2: Generate API Keys

### For Demo Trading (Recommended First)

1. **Access Demo API Management**
   - Log into demo environment
   - Navigate to Profile → API Management
   - Click "Create V5 API Key"

2. **Configure API Key Settings**
   - **API Key Name**: "Trading Bot Demo"
   - **Passphrase**: Create a strong passphrase (save securely)
   - **IP Whitelist**: Add your server's IP address (optional but recommended)
   - **Permissions**: Select "Trade" only (uncheck Withdraw and Funding)

3. **Complete 2FA Verification**
   - Enter Google Authenticator code
   - Enter email verification code
   - Click "Confirm"

4. **Save API Credentials**
   - **API Key**: Copy and save securely
   - **Secret Key**: Copy and save securely (shown only once)
   - **Passphrase**: The one you created above

### For Live Trading (After Testing)

1. **Access Live API Management**
   - Log into main OKX account
   - Navigate to Profile → API Management
   - Click "Create V5 API Key"

2. **Configure Live API Key**
   - **API Key Name**: "Trading Bot Live"
   - **Passphrase**: Create a different passphrase from demo
   - **IP Whitelist**: Your production server IP
   - **Permissions**: "Trade" only
   - **Sub-account**: Create dedicated sub-account (recommended)

3. **Fund Trading Account**
   - Transfer your £500 capital to trading account
   - Keep funds in sub-account for isolation
   - Never risk more than you can afford to lose

## Step 3: Configure API Security

### Create Sub-Account (Recommended)

1. **Create Sub-Account**
   - Go to Account → Sub-account Management
   - Click "Create Sub-account"
   - Name: "TradingBot"
   - Type: "Trading"

2. **Transfer Funds to Sub-Account**
   - Transfer your £500 trading capital
   - Keep main account funds separate
   - Set up automatic profit withdrawal if desired

3. **Generate Sub-Account API Key**
   - Switch to sub-account view
   - Create API key specifically for sub-account
   - Use restrictive permissions

### IP Whitelisting Setup

1. **Find Your Server IP**
   ```bash
   # From your WSL/Ubuntu terminal
   curl ifconfig.me
   ```

2. **Add IP to Whitelist**
   - In API key settings, add your IP address
   - Format: `123.456.789.012` (single IP)
   - Or range: `123.456.789.0/24` (subnet)

3. **Update IP When Changed**
   - Monitor for IP changes
   - Update whitelist when necessary
   - Consider using VPS with static IP

### Permission Configuration

**Recommended Permissions for Trading Bot:**
- ✅ **Trade**: Required for buy/sell orders
- ❌ **Withdraw**: Never enable for automated trading
- ❌ **Funding**: Not needed for spot trading
- ❌ **Transfer**: Not needed if using sub-account

## Step 4: Test API Connection

### Install Required Libraries

```bash
# Activate your virtual environment
source ~/okx_trading_bot/venv/bin/activate

# Install OKX SDK and dependencies
pip install okx requests python-dotenv
```

### Create Test Script

1. **Create API Test File**
   ```bash
   nano ~/okx_trading_bot/test_okx_api.py
   ```

2. **Add Test Code**
   ```python
   import okx.Account as Account
   import okx.Trade as Trade
   import okx.MarketData as MarketData
   import json
   from datetime import datetime
   
   # API Configuration (Demo)
   API_KEY = "your_demo_api_key"
   SECRET_KEY = "your_demo_secret_key"
   PASSPHRASE = "your_demo_passphrase"
   BASE_URL = "https://www.okx.com"  # Demo: use demo URL
   FLAG = "0"  # 0: Demo, 1: Live
   
   def test_api_connection():
       """Test basic API connectivity"""
       try:
           # Initialize API clients
           account_api = Account.AccountAPI(API_KEY, SECRET_KEY, PASSPHRASE, False, FLAG)
           trade_api = Trade.TradeAPI(API_KEY, SECRET_KEY, PASSPHRASE, False, FLAG)
           market_api = MarketData.MarketAPI(API_KEY, SECRET_KEY, PASSPHRASE, False, FLAG)
           
           print("🔄 Testing API Connection...")
           
           # Test 1: Get account balance
           print("\n1. Testing Account Balance...")
           balance = account_api.get_account_balance()
           if balance['code'] == '0':
               print("✅ Account balance retrieved successfully")
               for item in balance['data']:
                   for detail in item['details']:
                       if float(detail['cashBal']) > 0:
                           print(f"   {detail['ccy']}: {detail['cashBal']}")
           else:
               print(f"❌ Balance error: {balance['msg']}")
           
           # Test 2: Get market data
           print("\n2. Testing Market Data...")
           ticker = market_api.get_ticker("BTC-USDT")
           if ticker['code'] == '0':
               print("✅ Market data retrieved successfully")
               price = ticker['data'][0]['last']
               print(f"   BTC-USDT Price: ${price}")
           else:
               print(f"❌ Market data error: {ticker['msg']}")
           
           # Test 3: Get trading instruments
           print("\n3. Testing Trading Instruments...")
           instruments = trade_api.get_instruments("SPOT")
           if instruments['code'] == '0':
               print(f"✅ Found {len(instruments['data'])} trading pairs")
           else:
               print(f"❌ Instruments error: {instruments['msg']}")
           
           # Test 4: Check positions (should be empty initially)
           print("\n4. Testing Positions...")
           positions = account_api.get_positions()
           if positions['code'] == '0':
               print(f"✅ Positions retrieved: {len(positions['data'])} active")
           else:
               print(f"❌ Positions error: {positions['msg']}")
           
           print("\n🎉 All API tests completed successfully!")
           return True
           
       except Exception as e:
           print(f"❌ API Test Failed: {str(e)}")
           return False
   
   def test_demo_order():
       """Test placing a small demo order"""
       try:
           trade_api = Trade.TradeAPI(API_KEY, SECRET_KEY, PASSPHRASE, False, FLAG)
           
           print("\n🔄 Testing Demo Order Placement...")
           
           # Place a small buy order for BTC
           order_data = {
               "instId": "BTC-USDT",
               "tdMode": "cash",  # Spot trading
               "side": "buy",
               "ordType": "limit",
               "sz": "0.001",  # Very small amount
               "px": "30000"   # Low price (likely won't fill)
           }
           
           result = trade_api.place_order(**order_data)
           
           if result['code'] == '0':
               order_id = result['data'][0]['ordId']
               print(f"✅ Demo order placed successfully: {order_id}")
               
               # Cancel the order immediately
               cancel_result = trade_api.cancel_order("BTC-USDT", order_id)
               if cancel_result['code'] == '0':
                   print("✅ Demo order cancelled successfully")
               
               return True
           else:
               print(f"❌ Order placement failed: {result['msg']}")
               return False
               
       except Exception as e:
           print(f"❌ Demo order test failed: {str(e)}")
           return False
   
   if __name__ == "__main__":
       print("🚀 OKX API Connection Test")
       print("=" * 50)
       
       # Run basic tests
       if test_api_connection():
           # Run order test if basic tests pass
           test_demo_order()
       
       print("\n📝 Next Steps:")
       print("1. If tests passed, your API is configured correctly")
       print("2. Update your bot configuration with these credentials")
       print("3. Start with demo trading before going live")
       print("4. Monitor your first trades carefully")
   ```

3. **Update API Credentials**
   - Replace placeholder values with your actual demo API credentials
   - Never commit real credentials to version control

4. **Run Test**
   ```bash
   python test_okx_api.py
   ```

### Expected Test Results

```
🚀 OKX API Connection Test
==================================================

🔄 Testing API Connection...

1. Testing Account Balance...
✅ Account balance retrieved successfully
   USDT: 100000.0
   BTC: 1.0

2. Testing Market Data...
✅ Market data retrieved successfully
   BTC-USDT Price: $43250.5

3. Testing Trading Instruments...
✅ Found 400+ trading pairs

4. Testing Positions...
✅ Positions retrieved: 0 active

🎉 All API tests completed successfully!

🔄 Testing Demo Order Placement...
✅ Demo order placed successfully: 12345678901234567890
✅ Demo order cancelled successfully
```

## Step 5: Configure Bot API Settings

### Create Secure Configuration

1. **Create API Configuration File**
   ```bash
   nano ~/okx_trading_bot/config/okx_config.py
   ```

2. **Add Configuration Structure**
   ```python
   import os
   from dataclasses import dataclass
   from typing import Dict, List
   
   @dataclass
   class OKXConfig:
       # API Credentials (loaded from environment)
       api_key: str = ""
       secret_key: str = ""
       passphrase: str = ""
       
       # Environment Settings
       is_demo: bool = True  # Start with demo
       base_url: str = "https://www.okx.com"
       flag: str = "0"  # 0: Demo, 1: Live
       
       # Trading Parameters
       default_currency: str = "USDT"
       trading_pairs: List[str] = None
       max_position_size: float = 100.0  # Max USDT per position
       min_order_size: float = 5.0       # Min USDT per order
       
       # Risk Management
       max_daily_loss: float = 10.0      # Max £10 loss per day
       max_drawdown: float = 0.05        # 5% max drawdown
       position_limit: int = 3           # Max 3 concurrent positions
       
       # Rate Limiting
       requests_per_second: int = 10
       requests_per_minute: int = 600
       
       def __post_init__(self):
           if self.trading_pairs is None:
               self.trading_pairs = [
                   "BTC-USDT", "ETH-USDT", "ADA-USDT",
                   "DOT-USDT", "LINK-USDT", "SOL-USDT"
               ]
           
           # Load from environment variables
           self.api_key = os.getenv('OKX_API_KEY', self.api_key)
           self.secret_key = os.getenv('OKX_SECRET_KEY', self.secret_key)
           self.passphrase = os.getenv('OKX_PASSPHRASE', self.passphrase)
           
           # Validate required fields
           if not all([self.api_key, self.secret_key, self.passphrase]):
               raise ValueError("Missing required OKX API credentials")
   
   # Create global config instance
   okx_config = OKXConfig()
   ```

### Set Environment Variables

1. **Update .env File**
   ```bash
   nano ~/okx_trading_bot/.env
   ```

2. **Add OKX Credentials**
   ```bash
   # OKX API Configuration
   OKX_API_KEY=your_demo_api_key_here
   OKX_SECRET_KEY=your_demo_secret_key_here
   OKX_PASSPHRASE=your_demo_passphrase_here
   OKX_IS_DEMO=true
   OKX_BASE_URL=https://www.okx.com
   
   # Trading Parameters
   OKX_MAX_POSITION_SIZE=100.0
   OKX_MIN_ORDER_SIZE=5.0
   OKX_MAX_DAILY_LOSS=10.0
   OKX_POSITION_LIMIT=3
   ```

3. **Secure the .env File**
   ```bash
   chmod 600 ~/okx_trading_bot/.env
   ```

## Step 6: Implement API Wrapper

### Create OKX API Wrapper

1. **Create API Wrapper File**
   ```bash
   nano ~/okx_trading_bot/src/okx_client.py
   ```

2. **Add Wrapper Implementation**
   ```python
   import okx.Account as Account
   import okx.Trade as Trade
   import okx.MarketData as MarketData
   import time
   import logging
   from typing import Dict, List, Optional
   from dataclasses import dataclass
   from config.okx_config import okx_config
   
   @dataclass
   class OrderResult:
       success: bool
       order_id: str = ""
       error_message: str = ""
       data: Dict = None
   
   class OKXClient:
       def __init__(self):
           self.config = okx_config
           self.logger = logging.getLogger(__name__)
           
           # Initialize API clients
           self.account_api = Account.AccountAPI(
               self.config.api_key,
               self.config.secret_key,
               self.config.passphrase,
               False,  # Use HTTPS
               self.config.flag
           )
           
           self.trade_api = Trade.TradeAPI(
               self.config.api_key,
               self.config.secret_key,
               self.config.passphrase,
               False,
               self.config.flag
           )
           
           self.market_api = MarketData.MarketAPI(
               self.config.api_key,
               self.config.secret_key,
               self.config.passphrase,
               False,
               self.config.flag
           )
           
           # Rate limiting
           self.last_request_time = 0
           self.request_count = 0
           self.minute_start = time.time()
       
       def _rate_limit(self):
           """Implement rate limiting"""
           current_time = time.time()
           
           # Reset minute counter
           if current_time - self.minute_start > 60:
               self.request_count = 0
               self.minute_start = current_time
           
           # Check per-minute limit
           if self.request_count >= self.config.requests_per_minute:
               sleep_time = 60 - (current_time - self.minute_start)
               if sleep_time > 0:
                   time.sleep(sleep_time)
                   self.request_count = 0
                   self.minute_start = time.time()
           
           # Check per-second limit
           time_since_last = current_time - self.last_request_time
           min_interval = 1.0 / self.config.requests_per_second
           
           if time_since_last < min_interval:
               time.sleep(min_interval - time_since_last)
           
           self.last_request_time = time.time()
           self.request_count += 1
       
       def get_account_balance(self) -> Dict:
           """Get account balance"""
           self._rate_limit()
           try:
               result = self.account_api.get_account_balance()
               if result['code'] == '0':
                   return {
                       'success': True,
                       'data': result['data']
                   }
               else:
                   self.logger.error(f"Balance error: {result['msg']}")
                   return {
                       'success': False,
                       'error': result['msg']
                   }
           except Exception as e:
               self.logger.error(f"Balance exception: {str(e)}")
               return {
                   'success': False,
                   'error': str(e)
               }
       
       def get_ticker(self, symbol: str) -> Dict:
           """Get current ticker price"""
           self._rate_limit()
           try:
               result = self.market_api.get_ticker(symbol)
               if result['code'] == '0' and result['data']:
                   ticker_data = result['data'][0]
                   return {
                       'success': True,
                       'symbol': symbol,
                       'price': float(ticker_data['last']),
                       'bid': float(ticker_data['bidPx']),
                       'ask': float(ticker_data['askPx']),
                       'volume': float(ticker_data['vol24h']),
                       'change': float(ticker_data['chg24h'])
                   }
               else:
                   return {
                       'success': False,
                       'error': result.get('msg', 'No data')
                   }
           except Exception as e:
               self.logger.error(f"Ticker exception: {str(e)}")
               return {
                   'success': False,
                   'error': str(e)
               }
       
       def place_order(self, symbol: str, side: str, size: float, 
                      price: Optional[float] = None, order_type: str = "market") -> OrderResult:
           """Place a trading order"""
           self._rate_limit()
           
           try:
               order_data = {
                   "instId": symbol,
                   "tdMode": "cash",  # Spot trading
                   "side": side,
                   "ordType": order_type,
                   "sz": str(size)
               }
               
               if order_type == "limit" and price:
                   order_data["px"] = str(price)
               
               result = self.trade_api.place_order(**order_data)
               
               if result['code'] == '0':
                   order_id = result['data'][0]['ordId']
                   self.logger.info(f"Order placed: {order_id}")
                   return OrderResult(
                       success=True,
                       order_id=order_id,
                       data=result['data'][0]
                   )
               else:
                   self.logger.error(f"Order failed: {result['msg']}")
                   return OrderResult(
                       success=False,
                       error_message=result['msg']
                   )
                   
           except Exception as e:
               self.logger.error(f"Order exception: {str(e)}")
               return OrderResult(
                   success=False,
                   error_message=str(e)
               )
       
       def cancel_order(self, symbol: str, order_id: str) -> bool:
           """Cancel an existing order"""
           self._rate_limit()
           try:
               result = self.trade_api.cancel_order(symbol, order_id)
               return result['code'] == '0'
           except Exception as e:
               self.logger.error(f"Cancel order exception: {str(e)}")
               return False
       
       def get_positions(self) -> List[Dict]:
           """Get current positions"""
           self._rate_limit()
           try:
               result = self.account_api.get_positions()
               if result['code'] == '0':
                   return result['data']
               else:
                   self.logger.error(f"Positions error: {result['msg']}")
                   return []
           except Exception as e:
               self.logger.error(f"Positions exception: {str(e)}")
               return []
       
       def get_order_history(self, symbol: str = "", limit: int = 100) -> List[Dict]:
           """Get order history"""
           self._rate_limit()
           try:
               result = self.trade_api.get_orders_history(
                   instType="SPOT",
                   instId=symbol if symbol else "",
                   limit=str(limit)
               )
               if result['code'] == '0':
                   return result['data']
               else:
                   self.logger.error(f"Order history error: {result['msg']}")
                   return []
           except Exception as e:
               self.logger.error(f"Order history exception: {str(e)}")
               return []
   ```

## Step 7: Validate Configuration

### Run Comprehensive Test

1. **Create Validation Script**
   ```bash
   nano ~/okx_trading_bot/validate_okx.py
   ```

2. **Add Validation Code**
   ```python
   from src.okx_client import OKXClient
   import json
   
   def validate_okx_setup():
       """Comprehensive OKX setup validation"""
       print("🔍 Validating OKX Configuration...")
       print("=" * 50)
       
       try:
           client = OKXClient()
           
           # Test 1: Account Balance
           print("1. Testing account balance...")
           balance = client.get_account_balance()
           if balance['success']:
               print("✅ Account balance retrieved")
               total_usdt = 0
               for account in balance['data']:
                   for detail in account['details']:
                       if detail['ccy'] == 'USDT':
                           total_usdt = float(detail['cashBal'])
               print(f"   Available USDT: {total_usdt}")
           else:
               print(f"❌ Balance error: {balance['error']}")
               return False
           
           # Test 2: Market Data
           print("\n2. Testing market data...")
           ticker = client.get_ticker("BTC-USDT")
           if ticker['success']:
               print("✅ Market data retrieved")
               print(f"   BTC Price: ${ticker['price']}")
           else:
               print(f"❌ Market data error: {ticker['error']}")
               return False
           
           # Test 3: Trading Pairs
           print("\n3. Testing trading pairs...")
           for pair in client.config.trading_pairs[:3]:  # Test first 3
               ticker = client.get_ticker(pair)
               if ticker['success']:
                   print(f"   ✅ {pair}: ${ticker['price']}")
               else:
                   print(f"   ❌ {pair}: {ticker['error']}")
           
           # Test 4: Order Placement (Demo)
           if client.config.is_demo:
               print("\n4. Testing demo order...")
               order = client.place_order(
                   symbol="BTC-USDT",
                   side="buy",
                   size=0.001,
                   price=30000,
                   order_type="limit"
               )
               if order.success:
                   print(f"✅ Demo order placed: {order.order_id}")
                   # Cancel immediately
                   if client.cancel_order("BTC-USDT", order.order_id):
                       print("✅ Demo order cancelled")
               else:
                   print(f"❌ Demo order failed: {order.error_message}")
           
           print("\n🎉 OKX configuration validated successfully!")
           print("\n📋 Configuration Summary:")
           print(f"   Environment: {'Demo' if client.config.is_demo else 'Live'}")
           print(f"   Trading Pairs: {len(client.config.trading_pairs)}")
           print(f"   Max Position: ${client.config.max_position_size}")
           print(f"   Daily Loss Limit: ${client.config.max_daily_loss}")
           
           return True
           
       except Exception as e:
           print(f"❌ Validation failed: {str(e)}")
           return False
   
   if __name__ == "__main__":
       validate_okx_setup()
   ```

3. **Run Validation**
   ```bash
   python validate_okx.py
   ```

## Troubleshooting

### Common API Issues

**Authentication Errors**
```
Error: Invalid signature
```
- Check API key, secret, and passphrase are correct
- Ensure system time is synchronized
- Verify API key permissions

**Rate Limiting Errors**
```
Error: Too many requests
```
- Implement proper rate limiting in your code
- Reduce request frequency
- Use WebSocket for real-time data

**Permission Errors**
```
Error: Operation not allowed
```
- Check API key has "Trade" permission enabled
- Verify IP whitelist includes your server
- Ensure account has sufficient balance

**Network Errors**
```
Error: Connection timeout
```
- Check internet connectivity
- Verify firewall settings
- Try different DNS servers

### Debug Commands

```bash
# Test network connectivity
ping www.okx.com

# Check system time (important for API signatures)
date

# Test DNS resolution
nslookup www.okx.com

# Check environment variables
env | grep OKX

# Test Python imports
python -c "import okx; print('OKX SDK installed')"
```

### Security Checklist

- [ ] API keys stored in environment variables
- [ ] .env file has restricted permissions (600)
- [ ] IP whitelist configured
- [ ] Only "Trade" permission enabled
- [ ] Using sub-account for isolation
- [ ] Demo testing completed successfully
- [ ] Rate limiting implemented
- [ ] Error handling in place

## Going Live

### Transition from Demo to Live

1. **Complete Demo Testing**
   - Run bot for at least 24 hours in demo
   - Verify all functions work correctly
   - Check profit/loss calculations

2. **Create Live API Keys**
   - Generate new API keys for live trading
   - Use different passphrase from demo
   - Configure same IP whitelist

3. **Update Configuration**
   ```bash
   # Update .env file
   OKX_IS_DEMO=false
   OKX_API_KEY=your_live_api_key
   OKX_SECRET_KEY=your_live_secret_key
   OKX_PASSPHRASE=your_live_passphrase
   ```

4. **Start with Small Capital**
   - Begin with £50-100 for first week
   - Monitor performance closely
   - Gradually increase to full £500

## Next Steps

After completing OKX API configuration:

1. ✅ OKX account created and verified
2. ✅ API keys generated with proper permissions
3. ✅ Demo testing completed successfully
4. ✅ Security measures implemented
5. ➡️ Continue to [Bot Installation Guide](bot_installation.md)
6. ➡️ Review [Trading Strategy](trading_strategy.md)

---

**[Screenshot: OKX API Management page showing created API key with Trade permissions]**

**[Screenshot: Demo account balance showing virtual funds for testing]**

**[Screenshot: Successful API test results in terminal]**

**[Screenshot: OKX sub-account setup for trading isolation]**
