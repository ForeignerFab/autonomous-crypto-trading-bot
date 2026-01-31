
"""
OKX API Client
Handles all interactions with the OKX exchange API
"""

import asyncio
import aiohttp
import hmac
import hashlib
import base64
import json
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
from loguru import logger
import ccxt.async_support as ccxt


class OKXClient:
    """OKX exchange API client with rate limiting and error handling"""
    
    def __init__(self, config: Dict):
        """Initialize OKX client"""
        self.config = config
        self.okx_config = config['okx']
        self.base_currency = config.get('trading', {}).get('base_currency', 'USDT')
        
        # Rate limiting
        self.rate_limit_buffer = self.okx_config.get('rate_limit_buffer', 0.1)
        self.last_request_time = 0
        self.request_count = 0
        self.rate_limit_window = 2  # seconds
        
        # Initialize CCXT client
        self.exchange = None
        
        logger.info("OKX client initialized")
    
    async def initialize(self):
        """Initialize the exchange connection"""
        try:
            self.exchange = ccxt.okx({
                'apiKey': self.okx_config['api_key'],
                'secret': self.okx_config['secret_key'],
                'password': self.okx_config['passphrase'],
                'sandbox': self.okx_config.get('sandbox', True),
                'enableRateLimit': True,
                'timeout': self.okx_config.get('timeout', 30) * 1000,
                'options': {
                    'defaultType': 'spot',  # spot, margin, swap, future, option
                }
            })
            
            # Test connection
            await self.exchange.load_markets()
            balance = await self.exchange.fetch_balance()
            
            bal = balance.get(self.base_currency, {}).get('free', 0)
            logger.info(f"OKX client connected successfully. Available balance: {bal} {self.base_currency}")
            
        except Exception as e:
            logger.error(f"Failed to initialize OKX client: {e}")
            raise
    
    async def close(self):
        """Close the exchange connection"""
        if self.exchange:
            await self.exchange.close()
            logger.info("OKX client connection closed")
    
    async def _rate_limit_check(self):
        """Check and enforce rate limits"""
        current_time = time.time()
        
        # Reset counter if window has passed
        if current_time - self.last_request_time > self.rate_limit_window:
            self.request_count = 0
            self.last_request_time = current_time
        
        # Check if we're approaching rate limits
        if self.request_count >= 50:  # Conservative limit
            sleep_time = self.rate_limit_window - (current_time - self.last_request_time)
            if sleep_time > 0:
                logger.debug(f"Rate limit protection: sleeping for {sleep_time:.2f}s")
                await asyncio.sleep(sleep_time)
                self.request_count = 0
                self.last_request_time = time.time()
        
        self.request_count += 1
    
    async def get_trading_pairs(self) -> List[str]:
        """Get all available trading pairs"""
        try:
            await self._rate_limit_check()
            
            markets = await self.exchange.load_markets()
            
            # Filter for base currency pairs and active markets
            base_pairs = [
                symbol for symbol, market in markets.items()
                if market['quote'] == self.base_currency
                and market['active']
                and market['spot']
                and self._is_tradeable_market(market)
            ]
            
            logger.debug(f"Found {len(base_pairs)} {self.base_currency} trading pairs")
            return base_pairs
        
        except Exception as e:
            logger.error(f"Error getting trading pairs: {e}")
            return []

    def _is_tradeable_market(self, market: Dict) -> bool:
        """Check if market is live/tradeable based on exchange metadata"""
        info = market.get('info', {}) if isinstance(market, dict) else {}
        inst_state = info.get('state') or info.get('instState') or info.get('status')
        if inst_state:
            state = str(inst_state).lower()
            if state not in {'live', 'trading', 'enabled'}:
                return False
        return True
    
    async def get_ticker(self, symbol: str) -> Dict:
        """Get ticker information for a symbol"""
        try:
            await self._rate_limit_check()
            ticker = await self.exchange.fetch_ticker(symbol)
            return ticker
        except Exception as e:
            logger.error(f"Error getting ticker for {symbol}: {e}")
            return {}
    
    async def get_klines(self, symbol: str, timeframe: str = '1m', limit: int = 100) -> List:
        """Get candlestick data"""
        try:
            await self._rate_limit_check()
            
            ohlcv = await self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            return ohlcv
        
        except Exception as e:
            logger.error(f"Error getting klines for {symbol}: {e}")
            return []

    async def get_klines_since(self, symbol: str, timeframe: str, since_ms: int, limit: int = 100) -> List:
        """Get candlestick data starting from a timestamp (ms)"""
        try:
            await self._rate_limit_check()
            ohlcv = await self.exchange.fetch_ohlcv(symbol, timeframe, since=since_ms, limit=limit)
            return ohlcv
        except Exception as e:
            logger.error(f"Error getting klines for {symbol} since {since_ms}: {e}")
            return []
    
    async def get_order_book(self, symbol: str, limit: int = 20) -> Dict:
        """Get order book data"""
        try:
            await self._rate_limit_check()
            
            order_book = await self.exchange.fetch_order_book(symbol, limit)
            return order_book
        
        except Exception as e:
            logger.error(f"Error getting order book for {symbol}: {e}")
            return {}
    
    async def get_balance(self) -> float:
        """Get account balance in base currency"""
        try:
            await self._rate_limit_check()
            
            balance = await self.exchange.fetch_balance()
            base_balance = balance.get(self.base_currency, {}).get('free', 0)
            return float(base_balance)
        
        except Exception as e:
            logger.error(f"Error getting balance: {e}")
            return 0.0
    
    async def place_order(self, symbol: str, side: str, amount: float, 
                         price: Optional[float] = None, order_type: str = 'market',
                         params: Optional[Dict] = None) -> Optional[Dict]:
        """Place a trading order"""
        try:
            await self._rate_limit_check()
            params = params or {}
            
            # Validate parameters
            if amount <= 0:
                logger.error(f"Invalid amount: {amount}")
                return None
            
            # Place order
            if order_type == 'market':
                order = await self.exchange.create_market_order(symbol, side, amount, params=params)
            elif order_type == 'limit':
                if price is None:
                    logger.error("Price required for limit order")
                    return None
                order = await self.exchange.create_limit_order(symbol, side, amount, price, params=params)
            elif order_type == 'stop_market':
                if price is None:
                    logger.error("Stop price required for stop market order")
                    return None
                stop_params = dict(params)
                stop_params.update({'stopPrice': price, 'type': 'stop_market'})
                order = await self.exchange.create_order(symbol, 'market', side, amount, None, stop_params)
            else:
                logger.error(f"Unsupported order type: {order_type}")
                return None
            
            logger.info(f"Order placed: {side} {amount} {symbol} @ {price or 'market'} ({order_type})")
            return order
        
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            message = str(e)
            if "51155" in message:
                return {
                    "status": "rejected",
                    "error_code": "51155",
                    "reason": "compliance_restriction"
                }
            return None

    async def get_order(self, symbol: str, order_id: str) -> Optional[Dict]:
        """Fetch order status"""
        try:
            await self._rate_limit_check()
            return await self.exchange.fetch_order(order_id, symbol)
        except Exception as e:
            logger.error(f"Error fetching order {order_id} for {symbol}: {e}")
            return None

    async def wait_for_order_fill(
        self,
        symbol: str,
        order_id: str,
        timeout: int = 10,
        poll_interval: float = 1.0
    ) -> Optional[Dict]:
        """Poll order status until filled or timeout"""
        try:
            start = time.time()
            while time.time() - start < timeout:
                order = await self.get_order(symbol, order_id)
                if not order:
                    await asyncio.sleep(poll_interval)
                    continue

                status = str(order.get("status", "")).lower()
                filled = float(order.get("filled") or 0)
                amount = float(order.get("amount") or 0)
                if status in {"closed", "filled"} or (amount and filled >= amount):
                    return order

                await asyncio.sleep(poll_interval)
            return await self.get_order(symbol, order_id)
        except Exception as e:
            logger.error(f"Error waiting for order fill {order_id}: {e}")
            return None
    
    async def cancel_order(self, order_id: str, symbol: str) -> bool:
        """Cancel an order"""
        try:
            await self._rate_limit_check()
            
            result = await self.exchange.cancel_order(order_id, symbol)
            logger.info(f"Order cancelled: {order_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error cancelling order {order_id}: {e}")
            return False
    
    async def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict]:
        """Get open orders"""
        try:
            await self._rate_limit_check()
            
            orders = await self.exchange.fetch_open_orders(symbol)
            return orders
        
        except Exception as e:
            logger.error(f"Error getting open orders: {e}")
            return []

    async def get_top_usdt_pairs(self, limit: int = 30) -> List[str]:
        """Get top base currency pairs by 24h quote volume"""
        try:
            await self._rate_limit_check()
            markets = await self.exchange.load_markets()
            tickers = await self.exchange.fetch_tickers()

            scored = []
            for symbol, ticker in tickers.items():
                market = markets.get(symbol)
                if not market or not market.get('spot'):
                    continue
                if not market.get('active'):
                    continue
                if not self._is_tradeable_market(market):
                    continue
                if market.get('quote') != self.base_currency:
                    continue

                quote_vol = ticker.get('quoteVolume') or 0
                scored.append((symbol, quote_vol))

            scored.sort(key=lambda x: x[1], reverse=True)
            return [symbol for symbol, _ in scored[:limit]]
        except Exception as e:
            logger.error(f"Error getting top USDT pairs: {e}")
            return []
    
    async def get_order_status(self, order_id: str, symbol: str) -> Optional[Dict]:
        """Get order status"""
        try:
            await self._rate_limit_check()
            
            order = await self.exchange.fetch_order(order_id, symbol)
            return order
        
        except Exception as e:
            logger.error(f"Error getting order status: {e}")
            return None
    
    async def get_positions(self) -> List[Dict]:
        """Get open positions"""
        try:
            await self._rate_limit_check()
            
            positions = await self.exchange.fetch_positions()
            # Filter out zero positions
            active_positions = [pos for pos in positions if float(pos.get('contracts', 0)) > 0]
            
            return active_positions
        
        except Exception as e:
            logger.error(f"Error getting positions: {e}")
            return []
    
    async def get_trade_history(self, symbol: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """Get trade history"""
        try:
            await self._rate_limit_check()
            
            trades = await self.exchange.fetch_my_trades(symbol, limit=limit)
            return trades
        
        except Exception as e:
            logger.error(f"Error getting trade history: {e}")
            return []
    
    async def get_account_info(self) -> Dict:
        """Get account information"""
        try:
            await self._rate_limit_check()
            
            balance = await self.exchange.fetch_balance()
            positions = await self.get_positions()
            
            # Calculate total equity
            total_equity = 0
            for currency, bal in balance.items():
                if currency != 'info' and bal.get('total', 0) > 0:
                    # Convert to USDT value (simplified)
                    if currency == 'USDT':
                        total_equity += bal['total']
                    else:
                        # Would need to get current price for conversion
                        pass
            
            return {
                'balance': balance,
                'positions': positions,
                'total_equity': total_equity,
                'free_margin': balance.get('USDT', {}).get('free', 0)
            }
        
        except Exception as e:
            logger.error(f"Error getting account info: {e}")
            return {}
    
    async def get_market_data(self, symbol: str) -> Dict:
        """Get comprehensive market data for a symbol"""
        try:
            # Get multiple data points in parallel
            ticker_task = self.get_ticker(symbol)
            klines_task = self.get_klines(symbol, '1m', 100)
            orderbook_task = self.get_order_book(symbol)
            
            ticker, klines, orderbook = await asyncio.gather(
                ticker_task, klines_task, orderbook_task,
                return_exceptions=True
            )
            
            return {
                'ticker': ticker if not isinstance(ticker, Exception) else {},
                'klines': klines if not isinstance(klines, Exception) else [],
                'orderbook': orderbook if not isinstance(orderbook, Exception) else {}
            }
        
        except Exception as e:
            logger.error(f"Error getting market data for {symbol}: {e}")
            return {}
    
    async def health_check(self) -> bool:
        """Check if the connection to OKX is healthy"""
        try:
            await self._rate_limit_check()
            
            # Simple ping test
            await self.exchange.fetch_status()
            return True
        
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    async def get_trading_fees(self, symbol: str) -> Dict:
        """Get trading fees for a symbol"""
        try:
            await self._rate_limit_check()
            
            fees = await self.exchange.fetch_trading_fees()
            symbol_fees = fees.get(symbol, {})
            
            return {
                'maker': symbol_fees.get('maker', 0.001),
                'taker': symbol_fees.get('taker', 0.001)
            }
        
        except Exception as e:
            logger.error(f"Error getting trading fees: {e}")
            return {'maker': 0.001, 'taker': 0.001}  # Default fees
