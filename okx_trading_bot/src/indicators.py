
"""
Technical Indicators Module
Implements optimized technical analysis indicators for high-frequency trading
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
from loguru import logger


class TechnicalIndicators:
    """Technical analysis indicators optimized for HFT"""
    
    def __init__(self, config: Dict):
        """Initialize technical indicators with configuration"""
        self.config = config
        self.indicator_config = config['trading']['indicators']
        logger.info("Technical indicators initialized")
    
    async def calculate_all(self, df: pd.DataFrame) -> Dict:
        """Calculate all technical indicators"""
        try:
            indicators = {}
            
            # Ensure we have OHLCV data
            if len(df) < 50:
                logger.warning("Insufficient data for indicator calculation")
                return indicators
            
            # Price data
            high = df['high'].values
            low = df['low'].values
            close = df['close'].values
            volume = df['volume'].values
            
            # RSI - Optimized for HFT
            indicators['rsi'] = self._calculate_rsi(
                pd.Series(close, index=df.index), 
                self.indicator_config['rsi']['period']
            )
            
            # MACD - Fast parameters for HFT
            macd_line, macd_signal, macd_histogram = self._calculate_macd(
                pd.Series(close, index=df.index),
                self.indicator_config['macd']['fast_period'],
                self.indicator_config['macd']['slow_period'],
                self.indicator_config['macd']['signal_period']
            )
            indicators['macd_line'] = macd_line
            indicators['macd_signal'] = macd_signal
            indicators['macd_histogram'] = macd_histogram
            
            # Bollinger Bands - Tightened for HFT
            bb_upper, bb_middle, bb_lower = self._calculate_bollinger_bands(
                pd.Series(close, index=df.index),
                self.indicator_config['bollinger_bands']['period'],
                self.indicator_config['bollinger_bands']['std_dev']
            )
            indicators['bb_upper'] = bb_upper
            indicators['bb_middle'] = bb_middle
            indicators['bb_lower'] = bb_lower
            
            # Bollinger Band Width and %B
            indicators['bb_width'] = (indicators['bb_upper'] - indicators['bb_lower']) / indicators['bb_middle']
            indicators['bb_percent'] = (pd.Series(close, index=df.index) - indicators['bb_lower']) / (indicators['bb_upper'] - indicators['bb_lower'])
            
            # EMAs - Fast and slow for trend detection
            indicators['ema_short'] = self._calculate_ema(
                pd.Series(close, index=df.index),
                self.indicator_config['ema']['short_period']
            )
            indicators['ema_long'] = self._calculate_ema(
                pd.Series(close, index=df.index),
                self.indicator_config['ema']['long_period']
            )
            
            # Volume indicators
            indicators['vwap'] = self._calculate_vwap(df)
            indicators['obv'] = self._calculate_obv(pd.Series(close, index=df.index), pd.Series(volume, index=df.index))
            indicators['volume_sma'] = self._calculate_sma(pd.Series(volume, index=df.index), 20)
            
            # Volatility indicators
            indicators['atr'] = self._calculate_atr(
                pd.Series(high, index=df.index),
                pd.Series(low, index=df.index),
                pd.Series(close, index=df.index),
                14
            )
            indicators['volatility'] = pd.Series(close, index=df.index).pct_change().rolling(20).std()
            
            # Momentum indicators
            indicators['roc'] = self._calculate_roc(pd.Series(close, index=df.index), 10)
            indicators['momentum'] = self._calculate_momentum(pd.Series(close, index=df.index), 10)
            
            # Stochastic oscillator
            stoch_k, stoch_d = self._calculate_stochastic(
                pd.Series(high, index=df.index),
                pd.Series(low, index=df.index),
                pd.Series(close, index=df.index)
            )
            indicators['stoch_k'] = stoch_k
            indicators['stoch_d'] = stoch_d
            
            # Williams %R
            indicators['williams_r'] = self._calculate_williams_r(
                pd.Series(high, index=df.index),
                pd.Series(low, index=df.index),
                pd.Series(close, index=df.index),
                14
            )
            
            # Commodity Channel Index
            indicators['cci'] = self._calculate_cci(
                pd.Series(high, index=df.index),
                pd.Series(low, index=df.index),
                pd.Series(close, index=df.index),
                14
            )
            
            # Money Flow Index
            indicators['mfi'] = self._calculate_mfi(
                pd.Series(high, index=df.index),
                pd.Series(low, index=df.index),
                pd.Series(close, index=df.index),
                pd.Series(volume, index=df.index),
                14
            )
            
            # Support and Resistance levels
            indicators.update(self._calculate_support_resistance(df))
            
            # Pattern recognition
            indicators.update(self._detect_patterns(df))
            
            # Market structure
            indicators.update(self._analyze_market_structure(df))
            
            return indicators
        
        except Exception as e:
            logger.error(f"Error calculating indicators: {e}")
            return {}
    
    def _calculate_vwap(self, df: pd.DataFrame) -> pd.Series:
        """Calculate Volume Weighted Average Price"""
        try:
            typical_price = (df['high'] + df['low'] + df['close']) / 3
            vwap_period = self.indicator_config['volume']['vwap_period']
            
            # Rolling VWAP calculation
            vwap = (typical_price * df['volume']).rolling(vwap_period).sum() / df['volume'].rolling(vwap_period).sum()
            return vwap
        except Exception as e:
            logger.error(f"Error calculating VWAP: {e}")
            return pd.Series(index=df.index)
    
    def _calculate_support_resistance(self, df: pd.DataFrame) -> Dict:
        """Calculate dynamic support and resistance levels"""
        try:
            indicators = {}
            
            # Pivot points
            high = df['high'].rolling(5).max()
            low = df['low'].rolling(5).min()
            
            # Support levels (recent lows)
            indicators['support_1'] = low.rolling(20).min()
            indicators['support_2'] = low.rolling(50).min()
            
            # Resistance levels (recent highs)
            indicators['resistance_1'] = high.rolling(20).max()
            indicators['resistance_2'] = high.rolling(50).max()
            
            # Fibonacci retracement levels
            recent_high = df['high'].rolling(50).max()
            recent_low = df['low'].rolling(50).min()
            diff = recent_high - recent_low
            
            indicators['fib_23.6'] = recent_high - (diff * 0.236)
            indicators['fib_38.2'] = recent_high - (diff * 0.382)
            indicators['fib_50.0'] = recent_high - (diff * 0.500)
            indicators['fib_61.8'] = recent_high - (diff * 0.618)
            
            return indicators
        except Exception as e:
            logger.error(f"Error calculating support/resistance: {e}")
            return {}
    
    def _detect_patterns(self, df: pd.DataFrame) -> Dict:
        """Detect candlestick and chart patterns"""
        try:
            indicators = {}
            
            high = df['high'].values
            low = df['low'].values
            open_price = df['open'].values
            close = df['close'].values
            
            # Candlestick patterns
            indicators['doji'] = self._detect_doji(
                pd.Series(open_price, index=df.index),
                pd.Series(high, index=df.index),
                pd.Series(low, index=df.index),
                pd.Series(close, index=df.index)
            )
            indicators['hammer'] = self._detect_hammer(
                pd.Series(open_price, index=df.index),
                pd.Series(high, index=df.index),
                pd.Series(low, index=df.index),
                pd.Series(close, index=df.index)
            )
            indicators['engulfing'] = self._detect_engulfing(
                pd.Series(open_price, index=df.index),
                pd.Series(high, index=df.index),
                pd.Series(low, index=df.index),
                pd.Series(close, index=df.index)
            )
            
            # Chart patterns (simplified detection)
            indicators['higher_highs'] = self._detect_higher_highs(df)
            indicators['lower_lows'] = self._detect_lower_lows(df)
            indicators['double_top'] = self._detect_double_top(df)
            indicators['double_bottom'] = self._detect_double_bottom(df)
            
            return indicators
        except Exception as e:
            logger.error(f"Error detecting patterns: {e}")
            return {}
    
    def _detect_higher_highs(self, df: pd.DataFrame) -> pd.Series:
        """Detect higher highs pattern"""
        try:
            highs = df['high'].rolling(5).max()
            higher_highs = (highs > highs.shift(5)) & (highs.shift(5) > highs.shift(10))
            return higher_highs.astype(int)
        except:
            return pd.Series(0, index=df.index)
    
    def _detect_lower_lows(self, df: pd.DataFrame) -> pd.Series:
        """Detect lower lows pattern"""
        try:
            lows = df['low'].rolling(5).min()
            lower_lows = (lows < lows.shift(5)) & (lows.shift(5) < lows.shift(10))
            return lower_lows.astype(int)
        except:
            return pd.Series(0, index=df.index)
    
    def _detect_double_top(self, df: pd.DataFrame) -> pd.Series:
        """Detect double top pattern"""
        try:
            highs = df['high'].rolling(10).max()
            double_top = (
                (abs(highs - highs.shift(20)) / highs < 0.02) &  # Similar highs
                (df['high'].rolling(10).min().shift(10) < highs * 0.95)  # Valley between
            )
            return double_top.astype(int)
        except:
            return pd.Series(0, index=df.index)
    
    def _detect_double_bottom(self, df: pd.DataFrame) -> pd.Series:
        """Detect double bottom pattern"""
        try:
            lows = df['low'].rolling(10).min()
            double_bottom = (
                (abs(lows - lows.shift(20)) / lows < 0.02) &  # Similar lows
                (df['low'].rolling(10).max().shift(10) > lows * 1.05)  # Peak between
            )
            return double_bottom.astype(int)
        except:
            return pd.Series(0, index=df.index)
    
    def _analyze_market_structure(self, df: pd.DataFrame) -> Dict:
        """Analyze market structure and trends"""
        try:
            indicators = {}
            
            # Trend strength
            close_prices = df['close']
            sma_20 = close_prices.rolling(20).mean()
            sma_50 = close_prices.rolling(50).mean()
            
            indicators['trend_strength'] = (close_prices - sma_20) / sma_20
            indicators['trend_direction'] = np.where(sma_20 > sma_50, 1, -1)
            
            # Market volatility regime
            returns = close_prices.pct_change()
            volatility = returns.rolling(20).std()
            vol_percentile = volatility.rolling(100).rank(pct=True)
            
            indicators['volatility_regime'] = np.where(vol_percentile > 0.8, 2,  # High vol
                                                     np.where(vol_percentile < 0.2, 0, 1))  # Low vol, Normal vol
            
            # Price momentum
            indicators['price_momentum'] = close_prices / close_prices.shift(10) - 1
            
            # Volume momentum
            volume_sma = df['volume'].rolling(20).mean()
            indicators['volume_momentum'] = df['volume'] / volume_sma - 1
            
            return indicators
        except Exception as e:
            logger.error(f"Error analyzing market structure: {e}")
            return {}
    
    def get_signal_strength(self, indicators: Dict, symbol: str) -> float:
        """Calculate overall signal strength from indicators"""
        try:
            if not indicators:
                return 0.0
            
            signals = []
            
            # RSI signal
            rsi = indicators.get('rsi', pd.Series()).iloc[-1] if len(indicators.get('rsi', pd.Series())) > 0 else 50
            if rsi < 30:
                signals.append(1.0)  # Strong buy
            elif rsi < 40:
                signals.append(0.5)  # Weak buy
            elif rsi > 70:
                signals.append(-1.0)  # Strong sell
            elif rsi > 60:
                signals.append(-0.5)  # Weak sell
            else:
                signals.append(0.0)  # Neutral
            
            # MACD signal
            macd_hist = indicators.get('macd_histogram', pd.Series())
            if len(macd_hist) > 1:
                if macd_hist.iloc[-1] > 0 and macd_hist.iloc[-2] <= 0:
                    signals.append(1.0)  # Bullish crossover
                elif macd_hist.iloc[-1] < 0 and macd_hist.iloc[-2] >= 0:
                    signals.append(-1.0)  # Bearish crossover
                else:
                    signals.append(0.0)
            
            # Bollinger Bands signal
            bb_percent = indicators.get('bb_percent', pd.Series())
            if len(bb_percent) > 0:
                bb_val = bb_percent.iloc[-1]
                if bb_val < 0.1:
                    signals.append(1.0)  # Oversold
                elif bb_val > 0.9:
                    signals.append(-1.0)  # Overbought
                else:
                    signals.append(0.0)
            
            # Volume confirmation
            volume_momentum = indicators.get('volume_momentum', pd.Series())
            if len(volume_momentum) > 0:
                vol_mom = volume_momentum.iloc[-1]
                if vol_mom > 0.5:
                    signals.append(0.5)  # High volume confirmation
                elif vol_mom < -0.5:
                    signals.append(-0.5)  # Low volume warning
                else:
                    signals.append(0.0)
            
            # Calculate weighted average
            if signals:
                return np.mean(signals)
            else:
                return 0.0
        
        except Exception as e:
            logger.error(f"Error calculating signal strength: {e}")
            return 0.0
    
    # Manual Technical Indicator Implementations
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI manually"""
        try:
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi
        except Exception as e:
            logger.error(f"Error calculating RSI: {e}")
            return pd.Series(index=prices.index)
    
    def _calculate_ema(self, prices: pd.Series, period: int) -> pd.Series:
        """Calculate Exponential Moving Average"""
        try:
            return prices.ewm(span=period, adjust=False).mean()
        except Exception as e:
            logger.error(f"Error calculating EMA: {e}")
            return pd.Series(index=prices.index)
    
    def _calculate_sma(self, prices: pd.Series, period: int) -> pd.Series:
        """Calculate Simple Moving Average"""
        try:
            return prices.rolling(window=period).mean()
        except Exception as e:
            logger.error(f"Error calculating SMA: {e}")
            return pd.Series(index=prices.index)
    
    def _calculate_macd(self, prices: pd.Series, fast: int, slow: int, signal: int) -> tuple:
        """Calculate MACD"""
        try:
            ema_fast = self._calculate_ema(prices, fast)
            ema_slow = self._calculate_ema(prices, slow)
            macd_line = ema_fast - ema_slow
            signal_line = self._calculate_ema(macd_line, signal)
            histogram = macd_line - signal_line
            return macd_line, signal_line, histogram
        except Exception as e:
            logger.error(f"Error calculating MACD: {e}")
            return pd.Series(index=prices.index), pd.Series(index=prices.index), pd.Series(index=prices.index)
    
    def _calculate_bollinger_bands(self, prices: pd.Series, period: int, std_dev: float) -> tuple:
        """Calculate Bollinger Bands"""
        try:
            sma = self._calculate_sma(prices, period)
            std = prices.rolling(window=period).std()
            upper_band = sma + (std * std_dev)
            lower_band = sma - (std * std_dev)
            return upper_band, sma, lower_band
        except Exception as e:
            logger.error(f"Error calculating Bollinger Bands: {e}")
            return pd.Series(index=prices.index), pd.Series(index=prices.index), pd.Series(index=prices.index)
    
    def _calculate_atr(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Average True Range"""
        try:
            prev_close = close.shift(1)
            tr1 = high - low
            tr2 = abs(high - prev_close)
            tr3 = abs(low - prev_close)
            true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr = true_range.rolling(window=period).mean()
            return atr
        except Exception as e:
            logger.error(f"Error calculating ATR: {e}")
            return pd.Series(index=high.index)
    
    def _calculate_obv(self, close: pd.Series, volume: pd.Series) -> pd.Series:
        """Calculate On-Balance Volume"""
        try:
            obv = pd.Series(index=close.index, dtype=float)
            obv.iloc[0] = volume.iloc[0]
            
            for i in range(1, len(close)):
                if close.iloc[i] > close.iloc[i-1]:
                    obv.iloc[i] = obv.iloc[i-1] + volume.iloc[i]
                elif close.iloc[i] < close.iloc[i-1]:
                    obv.iloc[i] = obv.iloc[i-1] - volume.iloc[i]
                else:
                    obv.iloc[i] = obv.iloc[i-1]
            
            return obv
        except Exception as e:
            logger.error(f"Error calculating OBV: {e}")
            return pd.Series(index=close.index)
    
    def _calculate_roc(self, prices: pd.Series, period: int) -> pd.Series:
        """Calculate Rate of Change"""
        try:
            roc = ((prices - prices.shift(period)) / prices.shift(period)) * 100
            return roc
        except Exception as e:
            logger.error(f"Error calculating ROC: {e}")
            return pd.Series(index=prices.index)
    
    def _calculate_momentum(self, prices: pd.Series, period: int) -> pd.Series:
        """Calculate Momentum"""
        try:
            momentum = prices - prices.shift(period)
            return momentum
        except Exception as e:
            logger.error(f"Error calculating Momentum: {e}")
            return pd.Series(index=prices.index)
    
    def _calculate_stochastic(self, high: pd.Series, low: pd.Series, close: pd.Series, k_period: int = 14, d_period: int = 3) -> tuple:
        """Calculate Stochastic Oscillator"""
        try:
            lowest_low = low.rolling(window=k_period).min()
            highest_high = high.rolling(window=k_period).max()
            k_percent = 100 * ((close - lowest_low) / (highest_high - lowest_low))
            d_percent = k_percent.rolling(window=d_period).mean()
            return k_percent, d_percent
        except Exception as e:
            logger.error(f"Error calculating Stochastic: {e}")
            return pd.Series(index=high.index), pd.Series(index=high.index)
    
    def _calculate_williams_r(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Williams %R"""
        try:
            highest_high = high.rolling(window=period).max()
            lowest_low = low.rolling(window=period).min()
            williams_r = -100 * ((highest_high - close) / (highest_high - lowest_low))
            return williams_r
        except Exception as e:
            logger.error(f"Error calculating Williams %R: {e}")
            return pd.Series(index=high.index)
    
    def _calculate_cci(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Commodity Channel Index"""
        try:
            typical_price = (high + low + close) / 3
            sma_tp = typical_price.rolling(window=period).mean()
            mean_deviation = typical_price.rolling(window=period).apply(lambda x: np.mean(np.abs(x - x.mean())))
            cci = (typical_price - sma_tp) / (0.015 * mean_deviation)
            return cci
        except Exception as e:
            logger.error(f"Error calculating CCI: {e}")
            return pd.Series(index=high.index)
    
    def _calculate_mfi(self, high: pd.Series, low: pd.Series, close: pd.Series, volume: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Money Flow Index"""
        try:
            typical_price = (high + low + close) / 3
            money_flow = typical_price * volume
            
            positive_flow = pd.Series(index=close.index, dtype=float)
            negative_flow = pd.Series(index=close.index, dtype=float)
            
            for i in range(1, len(typical_price)):
                if typical_price.iloc[i] > typical_price.iloc[i-1]:
                    positive_flow.iloc[i] = money_flow.iloc[i]
                    negative_flow.iloc[i] = 0
                elif typical_price.iloc[i] < typical_price.iloc[i-1]:
                    positive_flow.iloc[i] = 0
                    negative_flow.iloc[i] = money_flow.iloc[i]
                else:
                    positive_flow.iloc[i] = 0
                    negative_flow.iloc[i] = 0
            
            positive_mf = positive_flow.rolling(window=period).sum()
            negative_mf = negative_flow.rolling(window=period).sum()
            
            money_ratio = positive_mf / negative_mf
            mfi = 100 - (100 / (1 + money_ratio))
            
            return mfi
        except Exception as e:
            logger.error(f"Error calculating MFI: {e}")
            return pd.Series(index=high.index)
    
    def _detect_doji(self, open_price: pd.Series, high: pd.Series, low: pd.Series, close: pd.Series) -> pd.Series:
        """Detect Doji candlestick pattern"""
        try:
            body_size = abs(close - open_price)
            range_size = high - low
            doji = (body_size / range_size < 0.1).astype(int)
            return doji
        except Exception as e:
            logger.error(f"Error detecting Doji: {e}")
            return pd.Series(0, index=open_price.index)
    
    def _detect_hammer(self, open_price: pd.Series, high: pd.Series, low: pd.Series, close: pd.Series) -> pd.Series:
        """Detect Hammer candlestick pattern"""
        try:
            body_size = abs(close - open_price)
            upper_shadow = high - np.maximum(open_price, close)
            lower_shadow = np.minimum(open_price, close) - low
            
            hammer = (
                (lower_shadow > 2 * body_size) &
                (upper_shadow < 0.5 * body_size) &
                (body_size > 0)
            ).astype(int)
            
            return hammer
        except Exception as e:
            logger.error(f"Error detecting Hammer: {e}")
            return pd.Series(0, index=open_price.index)
    
    def _detect_engulfing(self, open_price: pd.Series, high: pd.Series, low: pd.Series, close: pd.Series) -> pd.Series:
        """Detect Engulfing candlestick pattern"""
        try:
            bullish_engulfing = (
                (close.shift(1) < open_price.shift(1)) &  # Previous candle bearish
                (close > open_price) &  # Current candle bullish
                (open_price < close.shift(1)) &  # Current open below previous close
                (close > open_price.shift(1))  # Current close above previous open
            ).astype(int)
            
            bearish_engulfing = (
                (close.shift(1) > open_price.shift(1)) &  # Previous candle bullish
                (close < open_price) &  # Current candle bearish
                (open_price > close.shift(1)) &  # Current open above previous close
                (close < open_price.shift(1))  # Current close below previous open
            ).astype(int)
            
            # Return 1 for bullish, -1 for bearish, 0 for none
            engulfing = bullish_engulfing - bearish_engulfing
            return engulfing
        except Exception as e:
            logger.error(f"Error detecting Engulfing: {e}")
            return pd.Series(0, index=open_price.index)
