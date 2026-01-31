
"""
Core Trading Engine
Implements the main trading logic with HFT strategies and technical analysis
"""

import asyncio
import time
import os
import json
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from loguru import logger
import yaml
from dotenv import load_dotenv
from datetime import datetime, timedelta

from .indicators import TechnicalIndicators
from .risk import RiskManager
from .okx_client import OKXClient
from .discord_bot import DiscordNotifier
from .ai_assistant import AIAssistant
from .database import DatabaseManager
from .research import PatternResearcher


@dataclass
class TradingSignal:
    """Trading signal data structure"""
    symbol: str
    action: str  # 'buy', 'sell', 'hold'
    confidence: float
    entry_price: float
    stop_loss: float
    take_profit: float
    position_size: float
    timestamp: datetime
    indicators: Dict
    reasoning: str


@dataclass
class Position:
    """Open position data structure"""
    symbol: str
    side: str
    size: float
    entry_price: float
    current_price: float
    stop_loss: float
    take_profit: float
    pnl: float
    timestamp: datetime


class TradingEngine:
    """Main trading engine implementing HFT strategies"""
    
    def __init__(self, config_path: str = "config.yml"):
        """Initialize trading engine"""
        self.config_path = config_path
        self.config = self._load_config(config_path)
        self.running = False
        self.trading_paused = False
        self.last_pair_selection = 0
        self.active_pairs = []
        self.positions = {}
        self.daily_pnl = 0.0
        self.total_trades = 0
        self.current_balance = None
        self.restricted_pairs = set()
        self.last_research_time = 0
        self.research_running = False
        
        # Initialize components
        self.indicators = TechnicalIndicators(self.config)
        self.risk_manager = RiskManager(self.config)
        self.okx_client = OKXClient(self.config)
        self.discord = DiscordNotifier(
            self.config,
            config_path=self.config_path,
            config_update_callback=self._apply_config_updates,
            ai_optimization_callback=self._run_ai_optimization,
            config_suggest_callback=self._run_research_config_suggest,
            status_callback=self._get_status,
            pause_callback=self._pause_trading,
            resume_callback=self._resume_trading,
            stop_callback=self._request_shutdown,
            balance_callback=self._get_balance,
            positions_callback=self._get_positions
        )
        self.ai_assistant = AIAssistant(self.config)
        self.db = DatabaseManager(self.config)
        self.researcher = PatternResearcher(
            self.config,
            self.okx_client,
            self.indicators,
            self.ai_assistant,
            self.db,
            self.discord
        )
        
        logger.info("Trading engine initialized")
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)

            # Load environment variables into config (OKX/Discord)
            load_dotenv()
            if 'okx' in config:
                config['okx']['api_key'] = os.getenv('OKX_API_KEY', config['okx'].get('api_key', ''))
                config['okx']['secret_key'] = os.getenv('OKX_SECRET_KEY', config['okx'].get('secret_key', ''))
                config['okx']['passphrase'] = os.getenv('OKX_PASSPHRASE', config['okx'].get('passphrase', ''))
            if 'discord' in config:
                config['discord']['bot_token'] = os.getenv('DISCORD_BOT_TOKEN', config['discord'].get('bot_token', ''))
                config['discord']['channel_id'] = os.getenv('DISCORD_CHANNEL_ID', config['discord'].get('channel_id', ''))
                config['discord']['webhook_url'] = os.getenv('DISCORD_WEBHOOK_URL', config['discord'].get('webhook_url', ''))

            logger.info(f"Configuration loaded from {config_path}")
            return config
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            raise

    def _log_ai_gate(self, signal: TradingSignal, evaluation: Dict):
        """Append AI gating decision to log file"""
        try:
            os.makedirs("logs", exist_ok=True)
            log_path = os.path.join("logs", "ai_gating.log")
            entry = {
                "timestamp": datetime.now().isoformat(),
                "symbol": signal.symbol,
                "action": signal.action,
                "approve": evaluation.get("approve", False),
                "confidence": evaluation.get("confidence", 0.0),
                "reason": evaluation.get("reason", "")
            }
            with open(log_path, "a") as log_file:
                log_file.write(json.dumps(entry) + "\n")
        except Exception as exc:
            logger.error(f"Failed to write AI gating log: {exc}")

    def _indicator_enabled(self, key: str, default: bool = True) -> bool:
        """Check if an indicator is enabled in config"""
        try:
            indicator_config = self.config.get('trading', {}).get('indicators', {})
            return bool(indicator_config.get(key, {}).get('enabled', default))
        except Exception:
            return default
    
    async def start(self):
        """Start the trading engine"""
        logger.info("Starting trading engine...")
        self.running = True
        
        # Initialize components
        await self.okx_client.initialize()
        await self._sync_live_balance("startup")
        await self.discord.initialize()
        await self.db.initialize()
        
        # Send startup notification
        base_currency = self.config.get('trading', {}).get('base_currency', 'USDT')
        await self.discord.send_notification(
            "🚀 Trading Bot Started",
            f"Bot initialized with {self.config['trading']['initial_capital']} {base_currency} capital\n"
            f"Risk per trade: {self.config['trading']['risk_per_trade']*100}%\n"
            f"Max risk: {self.config['trading']['max_risk_amount']} {base_currency}"
        )
        
        # Start main trading loop
        await self._main_loop()
    
    async def stop(self):
        """Stop the trading engine"""
        logger.info("Stopping trading engine...")
        self.running = False
        
        # Close all positions
        await self._close_all_positions()
        
        # Send shutdown notification
        await self.discord.send_notification(
            "🛑 Trading Bot Stopped",
            f"Final P&L: £{self.daily_pnl:.2f}\n"
            f"Total trades: {self.total_trades}"
        )
        
        # Cleanup
        await self.okx_client.close()
        await self.discord.close()
        await self.db.close()
    
    async def _main_loop(self):
        """Main trading loop"""
        while self.running:
            try:
                # Check if we need to update trading pairs
                if time.time() - self.last_pair_selection > self.config['trading']['pair_selection_interval']:
                    await self._update_trading_pairs()
                
                # Process each active pair (skip if paused)
                if not self.trading_paused:
                    for symbol in self.active_pairs:
                        await self._process_symbol(symbol)
                
                # Check existing positions
                await self._monitor_positions()
                
                # Risk management checks
                await self._risk_checks()
                
                # AI learning and optimization
                if self.config['ai_assistant']['enabled']:
                    await self._ai_optimization()

                # Pattern research (scheduled)
                await self._maybe_run_research()
                
                # Short sleep to prevent excessive CPU usage
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                await self.discord.send_error(f"Main loop error: {e}")
                await asyncio.sleep(5)
    
    async def _update_trading_pairs(self):
        """Update active trading pairs based on market conditions"""
        logger.info("Updating trading pairs...")
        
        try:
            # Get all available pairs
            all_pairs = await self.okx_client.get_trading_pairs()
            if self.restricted_pairs:
                all_pairs = [symbol for symbol in all_pairs if symbol not in self.restricted_pairs]
            
            # Filter pairs based on volume and volatility
            scored_pairs = []
            
            for symbol in all_pairs:
                try:
                    # Get recent market data
                    klines = await self.okx_client.get_klines(symbol, "1m", 100)
                    if len(klines) < 50:
                        continue
                    
                    df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                    df = df.astype(float)
                    
                    # Calculate scoring metrics
                    volatility = df['close'].pct_change().std() * 100
                    volume_avg = df['volume'].mean()
                    momentum = (df['close'].iloc[-1] / df['close'].iloc[-20] - 1) * 100
                    
                    # Score the pair (avoid log(0))
                    safe_volume = max(volume_avg, 1e-9)
                    score = (volatility * 0.4) + (np.log(safe_volume) * 0.3) + (abs(momentum) * 0.3)
                    
                    scored_pairs.append({
                        'symbol': symbol,
                        'score': score,
                        'volatility': volatility,
                        'volume': volume_avg,
                        'momentum': momentum
                    })
                    
                except Exception as e:
                    logger.warning(f"Error scoring pair {symbol}: {e}")
                    continue
            
            # Sort by score and select top pairs
            scored_pairs.sort(key=lambda x: x['score'], reverse=True)
            max_pairs = self.config['trading']['max_active_pairs']
            
            new_pairs = [pair['symbol'] for pair in scored_pairs[:max_pairs]]
            
            if new_pairs != self.active_pairs:
                self.active_pairs = new_pairs
                self.last_pair_selection = time.time()
                
                pair_info = "\n".join([
                    f"{pair['symbol']}: Score={pair['score']:.2f}, Vol={pair['volatility']:.2f}%, Mom={pair['momentum']:.2f}%"
                    for pair in scored_pairs[:max_pairs]
                ])
                
                await self.discord.send_notification(
                    "📊 Trading Pairs Updated",
                    f"Selected {len(new_pairs)} pairs:\n{pair_info}"
                )
                
                logger.info(f"Updated active pairs: {new_pairs}")
        
        except Exception as e:
            logger.error(f"Error updating trading pairs: {e}")
            await self.discord.send_error(f"Pair selection error: {e}")
    
    async def _process_symbol(self, symbol: str):
        """Process trading signals for a specific symbol"""
        try:
            # Get market data
            klines = await self.okx_client.get_klines(symbol, "1m", 100)
            if len(klines) < 50:
                return
            
            # Convert to DataFrame
            df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df = df.astype(float)
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            # Calculate technical indicators
            indicators = await self.indicators.calculate_all(df)
            
            # Generate trading signal
            signal = await self._generate_signal(symbol, df, indicators)
            
            if signal and signal.action in ['buy', 'sell']:
                # Check if we can execute the trade
                if await self._can_execute_trade(signal):
                    await self._execute_trade(signal)
        
        except Exception as e:
            logger.error(f"Error processing symbol {symbol}: {e}")
    
    async def _generate_signal(self, symbol: str, df: pd.DataFrame, indicators: Dict) -> Optional[TradingSignal]:
        """Generate trading signal based on technical analysis"""
        try:
            current_price = df['close'].iloc[-1]
            
            # Get indicator values
            rsi = indicators['rsi'].iloc[-1]
            macd_line = indicators['macd_line'].iloc[-1]
            macd_signal = indicators['macd_signal'].iloc[-1]
            macd_histogram = indicators['macd_histogram'].iloc[-1]
            bb_upper = indicators['bb_upper'].iloc[-1]
            bb_lower = indicators['bb_lower'].iloc[-1]
            bb_middle = indicators['bb_middle'].iloc[-1]
            ema_short = indicators['ema_short'].iloc[-1]
            ema_long = indicators['ema_long'].iloc[-1]
            vwap = indicators['vwap'].iloc[-1]
            
            # Signal generation logic
            indicator_signals = []
            reasoning = []
            
            # RSI signals
            if self._indicator_enabled('rsi'):
                if rsi < self.config['trading']['indicators']['rsi']['oversold']:
                    indicator_signals.append('buy')
                    reasoning.append(f"RSI oversold ({rsi:.2f})")
                elif rsi > self.config['trading']['indicators']['rsi']['overbought']:
                    indicator_signals.append('sell')
                    reasoning.append(f"RSI overbought ({rsi:.2f})")
            
            # MACD signals
            if self._indicator_enabled('macd'):
                if macd_line > macd_signal and macd_histogram > 0:
                    indicator_signals.append('buy')
                    reasoning.append("MACD bullish crossover")
                elif macd_line < macd_signal and macd_histogram < 0:
                    indicator_signals.append('sell')
                    reasoning.append("MACD bearish crossover")
            
            # Bollinger Bands signals
            if self._indicator_enabled('bollinger_bands'):
                if current_price < bb_lower:
                    indicator_signals.append('buy')
                    reasoning.append("Price below BB lower band")
                elif current_price > bb_upper:
                    indicator_signals.append('sell')
                    reasoning.append("Price above BB upper band")
            
            # EMA trend signals
            if self._indicator_enabled('ema'):
                if self._indicator_enabled('vwap'):
                    if ema_short > ema_long and current_price > vwap:
                        indicator_signals.append('buy')
                        reasoning.append("Bullish EMA trend + above VWAP")
                    elif ema_short < ema_long and current_price < vwap:
                        indicator_signals.append('sell')
                        reasoning.append("Bearish EMA trend + below VWAP")
                else:
                    if ema_short > ema_long:
                        indicator_signals.append('buy')
                        reasoning.append("Bullish EMA trend")
                    elif ema_short < ema_long:
                        indicator_signals.append('sell')
                        reasoning.append("Bearish EMA trend")

            # Stochastic oscillator signals
            if self._indicator_enabled('stochastic', default=False):
                stoch_k = indicators.get('stoch_k', pd.Series()).iloc[-1]
                stoch_d = indicators.get('stoch_d', pd.Series()).iloc[-1]
                stoch_config = self.config['trading']['indicators'].get('stochastic', {})
                stoch_overbought = stoch_config.get('overbought', 80)
                stoch_oversold = stoch_config.get('oversold', 20)
                if stoch_k < stoch_oversold and stoch_k > stoch_d:
                    indicator_signals.append('buy')
                    reasoning.append(f"Stochastic oversold ({stoch_k:.2f})")
                elif stoch_k > stoch_overbought and stoch_k < stoch_d:
                    indicator_signals.append('sell')
                    reasoning.append(f"Stochastic overbought ({stoch_k:.2f})")

            # Williams %R signals
            if self._indicator_enabled('williams_r', default=False):
                williams_r = indicators.get('williams_r', pd.Series()).iloc[-1]
                will_config = self.config['trading']['indicators'].get('williams_r', {})
                will_overbought = will_config.get('overbought', -20)
                will_oversold = will_config.get('oversold', -80)
                if williams_r < will_oversold:
                    indicator_signals.append('buy')
                    reasoning.append(f"Williams %R oversold ({williams_r:.2f})")
                elif williams_r > will_overbought:
                    indicator_signals.append('sell')
                    reasoning.append(f"Williams %R overbought ({williams_r:.2f})")

            # CCI signals
            if self._indicator_enabled('cci', default=False):
                cci = indicators.get('cci', pd.Series()).iloc[-1]
                cci_config = self.config['trading']['indicators'].get('cci', {})
                cci_overbought = cci_config.get('overbought', 100)
                cci_oversold = cci_config.get('oversold', -100)
                if cci < cci_oversold:
                    indicator_signals.append('buy')
                    reasoning.append(f"CCI oversold ({cci:.2f})")
                elif cci > cci_overbought:
                    indicator_signals.append('sell')
                    reasoning.append(f"CCI overbought ({cci:.2f})")
            
            ai_signal = None
            if self.ai_assistant:
                ai_signal = await self.ai_assistant.generate_signal_from_chart(symbol, df, indicators)
                if ai_signal:
                    reasoning.append(
                        f"AI signal: {ai_signal.get('action')} ({ai_signal.get('confidence', 0):.2f})"
                    )

            total_signals = len(indicator_signals) + (1 if ai_signal else 0)
            if self.config['trading']['strategy']['signal_confirmation']:
                if total_signals < 2:
                    return None

            # Weighted signal score
            scores = {"buy": 0.0, "sell": 0.0}
            for sig in indicator_signals:
                scores[sig] += 1.0
            if ai_signal:
                weight = float(ai_signal.get("weight", 1.0))
                confidence = float(ai_signal.get("confidence", 0.0))
                action = ai_signal.get("action")
                if action in scores:
                    scores[action] += weight * confidence
            
            # Determine final signal
            if scores["buy"] > scores["sell"]:
                action = 'buy'
            elif scores["sell"] > scores["buy"]:
                action = 'sell'
            else:
                return None

            total_score = scores["buy"] + scores["sell"]
            confidence = (scores[action] / total_score) if total_score else 0.0
            
            # Calculate position sizing and risk parameters
            atr = indicators['atr'].iloc[-1]
            atr_distance = 0.0
            if atr is not None and not np.isnan(atr) and atr > 0:
                atr_distance = atr * self.config['trading']['strategy']['stop_loss_multiplier']
            else:
                logger.warning(f"ATR invalid or zero for {symbol}; using min stop distance")

            min_stop_pct = float(self.config['risk_management'].get('min_stop_loss_pct', 0.005))
            max_stop_pct = float(self.config['risk_management'].get('max_stop_loss_pct', 0.1))
            min_distance = current_price * min_stop_pct
            max_distance = current_price * max_stop_pct

            stop_loss_distance = max(atr_distance, min_distance)
            stop_loss_distance = min(stop_loss_distance, max_distance)
            
            if action == 'buy':
                stop_loss = current_price - stop_loss_distance
                take_profit = current_price + (stop_loss_distance * self.config['trading']['strategy']['take_profit_multiplier'])
            else:
                stop_loss = current_price + stop_loss_distance
                take_profit = current_price - (stop_loss_distance * self.config['trading']['strategy']['take_profit_multiplier'])
            
            # Calculate position size
            position_size = self.risk_manager.calculate_position_size(
                current_price, stop_loss, self.config['trading']['max_risk_amount']
            )
            
            return TradingSignal(
                symbol=symbol,
                action=action,
                confidence=confidence,
                entry_price=current_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                position_size=position_size,
                timestamp=datetime.now(),
                indicators=indicators,
                reasoning="; ".join(reasoning)
            )
        
        except Exception as e:
            logger.error(f"Error generating signal for {symbol}: {e}")
            return None
    
    async def _can_execute_trade(self, signal: TradingSignal) -> bool:
        """Check if trade can be executed based on risk management"""
        try:
            # Check if we already have a position in this symbol
            if signal.symbol in self.positions:
                return False

            # Spot-only rule: do not open short positions without holdings
            if signal.action == 'sell' and signal.symbol not in self.positions:
                logger.info(f"Skipping short signal in spot mode: {signal.symbol}")
                return False
            
            # Check daily loss limit
            if self.daily_pnl <= -self.config['risk_management']['max_daily_loss']:
                logger.warning("Daily loss limit reached")
                return False
            
            # Check maximum positions
            if len(self.positions) >= self.config['risk_management']['max_positions']:
                return False
            
            # Check account balance
            balance = await self.okx_client.get_balance()
            if balance < signal.position_size * signal.entry_price:
                logger.warning("Insufficient balance for trade")
                return False
            
            # Additional risk checks
            risk_ok = await self.risk_manager.validate_trade(signal)
            if not risk_ok:
                return False

            # AI hard-gating checks
            ai_gating = self.config.get('ai_assistant', {}).get('trade_gating', {})
            if ai_gating.get('enabled', False) and self.ai_assistant:
                evaluation = await self.ai_assistant.evaluate_trade_signal(signal, signal.indicators)
                self._log_ai_gate(signal, evaluation)
                logger.info(
                    f"AI gate decision for {signal.symbol} {signal.action}: "
                    f"{'APPROVE' if evaluation.get('approve') else 'REJECT'} "
                    f"(confidence={evaluation.get('confidence', 0):.2f})"
                )
                await self.discord.send_ai_gating_log(signal, evaluation)
                if not evaluation.get('approve', False):
                    reason = evaluation.get('reason', 'AI gate rejected')
                    await self.discord.send_notification(
                        "🤖 AI Trade Gate Blocked",
                        f"Symbol: {signal.symbol}\nAction: {signal.action}\nReason: {reason}"
                    )
                    return False

            return True
        
        except Exception as e:
            logger.error(f"Error checking trade execution: {e}")
            return False
    
    async def _execute_trade(self, signal: TradingSignal):
        """Execute the trading signal"""
        try:
            if signal.symbol in self.restricted_pairs:
                logger.warning(f"Skipping restricted pair: {signal.symbol}")
                return

            notional = float(signal.position_size) * float(signal.entry_price)
            order_params = {}
            if signal.action == 'buy':
                order_params["cost"] = float(notional)

            # Place order
            order = await self.okx_client.place_order(
                symbol=signal.symbol,
                side=signal.action,
                amount=float(signal.position_size),
                price=float(signal.entry_price),
                order_type='market',
                params=order_params
            )
            
            if order and order.get('error_code') == '51155':
                self.restricted_pairs.add(signal.symbol)
                if signal.symbol in self.active_pairs:
                    self.active_pairs = [sym for sym in self.active_pairs if sym != signal.symbol]
                await self.discord.send_notification(
                    "🚫 Restricted Pair",
                    f"OKX rejected {signal.symbol} due to compliance restrictions. Removed from active pairs."
                )
                return

            if order and order.get('id') and order.get('status') not in ('filled', 'closed'):
                order = await self.okx_client.wait_for_order_fill(signal.symbol, order['id'])

            is_filled = False
            if order:
                status = str(order.get('status', '')).lower()
                filled = float(order.get('filled') or 0)
                amount = float(order.get('amount') or 0)
                is_filled = status in {'filled', 'closed'} or (amount and filled >= amount)

            if order and is_filled:
                # Create position record
                position = Position(
                    symbol=signal.symbol,
                    side=signal.action,
                    size=signal.position_size,
                    entry_price=signal.entry_price,
                    current_price=signal.entry_price,
                    stop_loss=signal.stop_loss,
                    take_profit=signal.take_profit,
                    pnl=0.0,
                    timestamp=datetime.now()
                )
                
                self.positions[signal.symbol] = position
                self.total_trades += 1
                
                # Place stop loss and take profit orders
                await self._place_exit_orders(position)
                
                # Log trade
                await self.db.log_trade(signal, order)
                
                # Send notification
                await self.discord.send_trade_notification(signal, order)

                # Update balance after trade execution
                await self._sync_live_balance("trade_open")
                
                logger.info(f"Executed {signal.action} order for {signal.symbol}: {signal.position_size} @ {signal.entry_price}")
            else:
                logger.warning(f"Order not filled for {signal.symbol}: {order}")
                await self.discord.send_notification(
                    "⚠️ Order Not Filled",
                    f"Symbol: {signal.symbol}\nAction: {signal.action}\nStatus: {order.get('status') if order else 'unknown'}"
                )
        
        except Exception as e:
            logger.error(f"Error executing trade: {e}")
            await self.discord.send_error(f"Trade execution error: {e}")
    
    async def _place_exit_orders(self, position: Position):
        """Place stop loss and take profit orders"""
        try:
            # Place stop loss
            await self.okx_client.place_order(
                symbol=position.symbol,
                side='sell' if position.side == 'buy' else 'buy',
                amount=position.size,
                price=position.stop_loss,
                order_type='stop_market'
            )
            
            # Place take profit
            await self.okx_client.place_order(
                symbol=position.symbol,
                side='sell' if position.side == 'buy' else 'buy',
                amount=position.size,
                price=position.take_profit,
                order_type='limit'
            )
        
        except Exception as e:
            logger.error(f"Error placing exit orders: {e}")
    
    async def _monitor_positions(self):
        """Monitor open positions and update P&L"""
        for symbol, position in list(self.positions.items()):
            try:
                # Get current price
                ticker = await self.okx_client.get_ticker(symbol)
                current_price = float(ticker['last'])
                
                # Update position
                position.current_price = current_price
                
                # Calculate P&L
                if position.side == 'buy':
                    position.pnl = (current_price - position.entry_price) * position.size
                else:
                    position.pnl = (position.entry_price - current_price) * position.size
                
                # Check if position should be closed
                await self._check_position_exit(position)
            
            except Exception as e:
                logger.error(f"Error monitoring position {symbol}: {e}")
    
    async def _check_position_exit(self, position: Position):
        """Check if position should be exited"""
        try:
            # Check stop loss
            if position.side == 'buy' and position.current_price <= position.stop_loss:
                await self._close_position(position, "Stop loss triggered")
            elif position.side == 'sell' and position.current_price >= position.stop_loss:
                await self._close_position(position, "Stop loss triggered")
            
            # Check take profit
            elif position.side == 'buy' and position.current_price >= position.take_profit:
                await self._close_position(position, "Take profit triggered")
            elif position.side == 'sell' and position.current_price <= position.take_profit:
                await self._close_position(position, "Take profit triggered")
        
        except Exception as e:
            logger.error(f"Error checking position exit: {e}")
    
    async def _close_position(self, position: Position, reason: str):
        """Close a position"""
        try:
            # Place closing order
            order = await self.okx_client.place_order(
                symbol=position.symbol,
                side='sell' if position.side == 'buy' else 'buy',
                amount=position.size,
                order_type='market'
            )
            
            if order and order.get('status') == 'filled':
                # Update daily P&L
                self.daily_pnl += position.pnl
                
                # Remove position
                del self.positions[position.symbol]
                
                # Log trade close
                await self.db.log_trade_close(position, order, reason)
                
                # Send notification
                await self.discord.send_position_close_notification(position, reason)

                # Update balance after trade close
                await self._sync_live_balance("trade_close")

                if self.ai_assistant:
                    self.ai_assistant.learn_from_trade({
                        "symbol": position.symbol,
                        "action": position.side,
                        "entry_price": position.entry_price,
                        "exit_price": position.current_price,
                        "pnl": position.pnl,
                        "indicators": {},
                        "patterns": []
                    })
                
                logger.info(f"Closed position {position.symbol}: P&L = £{position.pnl:.2f} ({reason})")
        
        except Exception as e:
            logger.error(f"Error closing position: {e}")
    
    async def _close_all_positions(self):
        """Close all open positions"""
        for position in list(self.positions.values()):
            await self._close_position(position, "Bot shutdown")
    
    async def _risk_checks(self):
        """Perform risk management checks"""
        try:
            # Check daily loss limit
            if self.daily_pnl <= -self.config['risk_management']['max_daily_loss']:
                await self.discord.send_notification(
                    "⚠️ Daily Loss Limit Reached",
                    f"Daily P&L: £{self.daily_pnl:.2f}\n"
                    f"Limit: £{self.config['risk_management']['max_daily_loss']}\n"
                    "Trading suspended for today."
                )
                # Stop trading for the day
                self.running = False
            
            # Check emergency stop
            total_pnl = await self.db.get_total_pnl()
            if total_pnl <= -self.config['risk_management']['max_drawdown']:
                await self.discord.send_notification(
                    "🚨 Emergency Stop Triggered",
                    f"Total drawdown: £{abs(total_pnl):.2f}\n"
                    "All positions will be closed."
                )
                await self._close_all_positions()
                self.running = False
        
        except Exception as e:
            logger.error(f"Error in risk checks: {e}")

    async def _sync_live_balance(self, reason: str):
        """Sync live account balance into capital tracking"""
        try:
            balance = await self.okx_client.get_balance()
            if balance and balance > 0:
                self.current_balance = float(balance)
                self.config['trading']['initial_capital'] = float(balance)
                self.risk_manager.update_initial_capital(balance)
                logger.info(f"Synced live balance ({reason}): {balance:.4f}")
        except Exception as e:
            logger.warning(f"Failed to sync live balance ({reason}): {e}")
    
    async def _ai_optimization(self):
        """AI-driven parameter optimization"""
        try:
            if self.ai_assistant:
                suggestions = await self.ai_assistant.analyze_performance()
                if suggestions:
                    await self.discord.send_ai_suggestions(suggestions)
        except Exception as e:
            logger.error(f"Error in AI optimization: {e}")

    async def _run_ai_optimization(self) -> Optional[Dict]:
        """Run AI optimization on-demand (Discord command hook)"""
        try:
            if not self.ai_assistant:
                return None
            return await self.ai_assistant.analyze_performance()
        except Exception as e:
            logger.error(f"Error running AI optimization: {e}")
            return None

    async def _run_research_config_suggest(self) -> Dict:
        """Generate config suggestions from research and render a chart"""
        try:
            records = await self.db.get_recent_pattern_research(hours=168, limit=3000)
            if not records:
                return {"suggestions": None, "chart_path": None, "message": "No recent research data found."}

            summary = self._aggregate_research_summary(records)
            chart_path = self._render_research_chart(summary)

            if not self.ai_assistant:
                return {
                    "suggestions": None,
                    "chart_path": chart_path,
                    "message": "AI assistant is not available."
                }

            suggestions = await self.ai_assistant.suggest_config_from_research(summary)
            return {
                "suggestions": suggestions,
                "chart_path": chart_path,
                "message": "Research-based config suggestions are ready."
            }
        except Exception as e:
            logger.error(f"Error generating research config suggestions: {e}")
            return {"suggestions": None, "chart_path": None, "message": f"Error: {e}"}

    def _aggregate_research_summary(self, records: List[Dict]) -> List[Dict]:
        """Aggregate research records by pattern and timeframe"""
        summary = {}
        for record in records:
            key = (record.get("pattern_name"), record.get("timeframe"))
            occurrences = int(record.get("occurrences", 0) or 0)
            success = float(record.get("success_rate", 0) or 0) * occurrences
            avg_ret = float(record.get("avg_return", 0) or 0) * occurrences
            if key not in summary:
                summary[key] = {"occurrences": 0, "success": 0.0, "avg_ret": 0.0}
            summary[key]["occurrences"] += occurrences
            summary[key]["success"] += success
            summary[key]["avg_ret"] += avg_ret

        results = []
        for (pattern, timeframe), data in summary.items():
            occ = data["occurrences"] or 1
            results.append({
                "pattern_name": pattern,
                "timeframe": timeframe,
                "occurrences": data["occurrences"],
                "success_rate": data["success"] / occ,
                "avg_return": data["avg_ret"] / occ
            })

        results.sort(key=lambda item: item.get("success_rate", 0), reverse=True)
        return results

    def _render_research_chart(self, summary: List[Dict]) -> Optional[str]:
        """Render a bar chart of research success rates"""
        if not summary:
            return None
        try:
            import matplotlib.pyplot as plt

            top = summary[:8]
            labels = [f"{item['pattern_name']} ({item['timeframe']})" for item in top]
            values = [item["success_rate"] * 100 for item in top]

            os.makedirs("logs", exist_ok=True)
            chart_path = os.path.join("logs", "research_summary.png")

            plt.figure(figsize=(10, 4))
            plt.bar(labels, values, color="#4C78A8")
            plt.ylabel("Success Rate (%)")
            plt.title("Top Pattern Success Rates (Recent Research)")
            plt.xticks(rotation=30, ha="right")
            plt.tight_layout()
            plt.savefig(chart_path, dpi=150)
            plt.close()

            return chart_path
        except Exception as e:
            logger.error(f"Error rendering research chart: {e}")
            return None

    async def _maybe_run_research(self):
        """Check schedule and start research if due"""
        settings = self.config.get('research', {})
        if not settings.get('enabled', False):
            return

        interval_hours = float(settings.get('interval_hours', 48))
        if time.time() - self.last_research_time < interval_hours * 3600:
            return

        if self.research_running:
            return

        self.research_running = True
        self.last_research_time = time.time()
        asyncio.create_task(self._run_research())

    async def _run_research(self):
        """Run pattern research asynchronously"""
        try:
            await self.discord.send_notification("📚 Research Started", "Running pattern research pipeline.")
            await self.researcher.run()
            await self.discord.send_notification("📚 Research Finished", "Pattern research completed.")
        except Exception as e:
            logger.error(f"Error running research: {e}")
            await self.discord.send_error(f"Research error: {e}")
        finally:
            self.research_running = False

    async def _get_balance(self) -> float:
        """Return current account balance"""
        try:
            return await self.okx_client.get_balance()
        except Exception as e:
            logger.error(f"Error fetching balance: {e}")
            return 0.0

    async def _get_positions(self) -> List[Dict]:
        """Return open positions"""
        return [
            {
                "symbol": position.symbol,
                "side": position.side,
                "size": position.size,
                "entry_price": position.entry_price,
                "current_price": position.current_price,
                "pnl": position.pnl
            }
            for position in self.positions.values()
        ]

    async def _get_status(self) -> Dict:
        """Return bot status for Discord"""
        return {
            "running": self.running,
            "paused": self.trading_paused,
            "daily_pnl": self.daily_pnl,
            "active_pairs": self.active_pairs,
            "open_positions": len(self.positions),
            "last_research": self.last_research_time
        }

    async def _pause_trading(self) -> bool:
        """Pause trading loop without shutting down"""
        self.trading_paused = True
        logger.info("Trading paused")
        return True

    async def _resume_trading(self) -> bool:
        """Resume trading loop"""
        self.trading_paused = False
        logger.info("Trading resumed")
        return True

    async def _request_shutdown(self) -> bool:
        """Request bot shutdown"""
        self.running = False
        logger.info("Shutdown requested")
        return True

    async def _apply_config_updates(self, updates: Dict) -> Dict:
        """Apply approved config updates and persist to config.yml"""
        allowed_params = {
            'rsi_period': ('trading', 'indicators', 'rsi', 'period'),
            'rsi_overbought': ('trading', 'indicators', 'rsi', 'overbought'),
            'rsi_oversold': ('trading', 'indicators', 'rsi', 'oversold'),
            'macd_fast_period': ('trading', 'indicators', 'macd', 'fast_period'),
            'macd_slow_period': ('trading', 'indicators', 'macd', 'slow_period'),
            'macd_signal_period': ('trading', 'indicators', 'macd', 'signal_period'),
            'bollinger_period': ('trading', 'indicators', 'bollinger_bands', 'period'),
            'bollinger_std_dev': ('trading', 'indicators', 'bollinger_bands', 'std_dev'),
            'risk_per_trade': ('trading', 'risk_per_trade')
            ,
            'enable_rsi': ('trading', 'indicators', 'rsi', 'enabled'),
            'enable_macd': ('trading', 'indicators', 'macd', 'enabled'),
            'enable_bollinger_bands': ('trading', 'indicators', 'bollinger_bands', 'enabled'),
            'enable_ema': ('trading', 'indicators', 'ema', 'enabled'),
            'enable_vwap': ('trading', 'indicators', 'vwap', 'enabled'),
            'enable_stochastic': ('trading', 'indicators', 'stochastic', 'enabled'),
            'enable_williams_r': ('trading', 'indicators', 'williams_r', 'enabled'),
            'enable_cci': ('trading', 'indicators', 'cci', 'enabled'),
            'stochastic_overbought': ('trading', 'indicators', 'stochastic', 'overbought'),
            'stochastic_oversold': ('trading', 'indicators', 'stochastic', 'oversold'),
            'williams_overbought': ('trading', 'indicators', 'williams_r', 'overbought'),
            'williams_oversold': ('trading', 'indicators', 'williams_r', 'oversold'),
            'cci_overbought': ('trading', 'indicators', 'cci', 'overbought'),
            'cci_oversold': ('trading', 'indicators', 'cci', 'oversold')
        }

        def get_nested_value(cfg: Dict, path: Tuple[str, ...]):
            current = cfg
            for key in path:
                if not isinstance(current, dict) or key not in current:
                    return None
                current = current[key]
            return current

        def set_nested_value(cfg: Dict, path: Tuple[str, ...], value):
            current = cfg
            for key in path[:-1]:
                if key not in current or not isinstance(current.get(key), dict):
                    current[key] = {}
                current = current[key]
            current[path[-1]] = value

        def coerce_value(new_value, existing_value):
            try:
                if isinstance(existing_value, bool):
                    return bool(new_value)
                if isinstance(existing_value, int):
                    return int(new_value)
                if isinstance(existing_value, float):
                    return float(new_value)
            except (ValueError, TypeError):
                return new_value
            return new_value

        applied = {}
        skipped = {}
        errors = []

        for param, suggestion in (updates or {}).items():
            if param not in allowed_params:
                skipped[param] = "Unsupported parameter"
                continue

            try:
                path = allowed_params[param]
                current_value = get_nested_value(self.config, path)
                suggested_value = suggestion.get('suggested') if isinstance(suggestion, dict) else suggestion
                new_value = coerce_value(suggested_value, current_value)

                if new_value == current_value:
                    skipped[param] = "No change"
                    continue

                set_nested_value(self.config, path, new_value)
                applied[param] = {"from": current_value, "to": new_value}
            except Exception as exc:
                errors.append(f"{param}: {exc}")

        if applied:
            try:
                with open(self.config_path, 'w') as file:
                    yaml.safe_dump(self.config, file, sort_keys=False)

                # Refresh cached config views in components
                self.indicators.indicator_config = self.config['trading']['indicators']
                self.risk_manager.trading_config = self.config['trading']
                self.risk_manager.risk_config = self.config['risk_management']
                self.ai_assistant.config = self.config

                # Append changelog entry
                os.makedirs("logs", exist_ok=True)
                changelog_path = os.path.join("logs", "config_changes.log")
                entry = {
                    "timestamp": datetime.now().isoformat(),
                    "applied": applied,
                    "skipped": skipped,
                    "errors": errors
                }
                with open(changelog_path, "a") as log_file:
                    log_file.write(json.dumps(entry) + "\n")

                await self.discord.send_config_change_log(entry)
            except Exception as exc:
                errors.append(f"Failed to write config: {exc}")

        return {"applied": applied, "skipped": skipped, "errors": errors}
