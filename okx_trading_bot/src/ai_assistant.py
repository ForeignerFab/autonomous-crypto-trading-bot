
"""
AI Assistant Module
Implements pattern recognition and self-learning mechanisms for parameter optimization
Enhanced with Ollama AI integration for free, powerful AI capabilities
"""

import numpy as np
import pandas as pd
import asyncio
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from loguru import logger
import json
import os
import pickle
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

# Import Ollama service
try:
    from .ollama_service import OllamaService
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    logger.warning("Ollama service not available - using fallback methods only")


@dataclass
class ParameterSuggestion:
    """Parameter optimization suggestion"""
    parameter: str
    current_value: Any
    suggested_value: Any
    confidence: float
    reason: str
    expected_improvement: float


@dataclass
class PatternMatch:
    """Market pattern match result"""
    pattern_name: str
    confidence: float
    historical_success_rate: float
    recommended_action: str
    risk_level: str


class AIAssistant:
    """AI-powered trading assistant for pattern recognition and optimization
    Enhanced with Ollama AI for free, powerful analysis capabilities"""
    
    def __init__(self, config: Dict):
        """Initialize AI assistant"""
        self.config = config
        self.ai_config = config.get('ai_assistant', {})
        self.enabled = self.ai_config.get('enabled', True)
        self.trade_gating_config = self.ai_config.get('trade_gating', {})
        self.trade_gating_enabled = self.trade_gating_config.get('enabled', False)
        
        if not self.enabled:
            logger.info("AI assistant disabled")
            return
        
        # Learning parameters
        self.learning_rate = self.ai_config.get('learning_rate', 0.01)
        self.min_confidence = self.ai_config.get('min_confidence', 0.7)
        self.lookback_period = self.ai_config.get('lookback_period', 30)
        
        # Initialize Ollama service (free AI)
        self.ollama = None
        self.use_ollama = self.ai_config.get('use_ollama', True) and OLLAMA_AVAILABLE
        
        if self.use_ollama:
            try:
                ollama_url = self.ai_config.get('ollama_url', None)
                ollama_model = os.getenv("OLLAMA_MODEL") or self.ai_config.get('ollama_model', 'llama3.2:7b')
                self.ollama = OllamaService(base_url=ollama_url, model=ollama_model)
                if self.ollama.is_available():
                    logger.info(f"Ollama AI enabled with model: {ollama_model}")
                else:
                    logger.warning("Ollama not available, using fallback methods")
                    self.use_ollama = False
            except Exception as e:
                logger.warning(f"Failed to initialize Ollama: {e}. Using fallback methods.")
                self.use_ollama = False
        
        # Models (fallback/legacy)
        self.performance_model = None
        self.pattern_model = None
        self.scaler = StandardScaler()
        
        # Data storage
        self.trade_history = []
        self.market_patterns = {}
        self.parameter_performance = {}
        self.research_stats = {}
        self._gate_lock = asyncio.Lock()
        
        # Pattern templates
        self.pattern_templates = self._initialize_pattern_templates()
        
        logger.info("AI assistant initialized" + (" with Ollama" if self.use_ollama else " (fallback mode)"))
    
    def _initialize_pattern_templates(self) -> Dict:
        """Initialize market pattern templates"""
        return {
            'bullish_divergence': {
                'description': 'Price makes lower low while RSI makes higher low',
                'success_rate': 0.65,
                'risk_level': 'medium',
                'action': 'buy'
            },
            'bearish_divergence': {
                'description': 'Price makes higher high while RSI makes lower high',
                'success_rate': 0.62,
                'risk_level': 'medium',
                'action': 'sell'
            },
            'bollinger_squeeze': {
                'description': 'Bollinger Bands contract indicating low volatility before breakout',
                'success_rate': 0.58,
                'risk_level': 'high',
                'action': 'wait_for_breakout'
            },
            'macd_golden_cross': {
                'description': 'MACD line crosses above signal line',
                'success_rate': 0.55,
                'risk_level': 'low',
                'action': 'buy'
            },
            'volume_spike': {
                'description': 'Volume significantly above average with price movement',
                'success_rate': 0.60,
                'risk_level': 'medium',
                'action': 'follow_trend'
            }
        }
    
    async def analyze_performance(self) -> Optional[Dict[str, ParameterSuggestion]]:
        """Analyze recent performance and suggest parameter optimizations
        Uses Ollama AI if available, falls back to traditional methods"""
        try:
            if not self.enabled:
                return None
            
            # Get recent trade data
            recent_trades = await self._get_recent_trades()
            if len(recent_trades) < 10:
                logger.info("Insufficient trade data for AI analysis")
                return None
            
            # Try Ollama AI first if available
            if self.use_ollama and self.ollama and self.ollama.is_available():
                try:
                    # Calculate performance metrics
                    performance_metrics = self._calculate_performance_metrics(recent_trades)
                    
                    # Use Ollama for intelligent analysis
                    ollama_analysis = self.ollama.analyze_trading_performance(
                        recent_trades, performance_metrics
                    )
                    
                    if ollama_analysis:
                        # Also get parameter optimization suggestions
                        current_params = {
                            'rsi_period': self.config['trading']['indicators']['rsi']['period'],
                            'macd_fast': self.config['trading']['indicators']['macd']['fast_period'],
                            'risk_per_trade': self.config['trading']['risk_per_trade'],
                            'bollinger_std': self.config['trading']['indicators']['bollinger_bands']['std_dev'],
                            'enable_rsi': self.config['trading']['indicators'].get('rsi', {}).get('enabled', True),
                            'enable_macd': self.config['trading']['indicators'].get('macd', {}).get('enabled', True),
                            'enable_bollinger_bands': self.config['trading']['indicators'].get('bollinger_bands', {}).get('enabled', True),
                            'enable_ema': self.config['trading']['indicators'].get('ema', {}).get('enabled', True),
                            'enable_vwap': self.config['trading']['indicators'].get('vwap', {}).get('enabled', True),
                            'enable_stochastic': self.config['trading']['indicators'].get('stochastic', {}).get('enabled', False),
                            'enable_williams_r': self.config['trading']['indicators'].get('williams_r', {}).get('enabled', False),
                            'enable_cci': self.config['trading']['indicators'].get('cci', {}).get('enabled', False)
                        }
                        
                        ollama_optimization = self.ollama.optimize_parameters(
                            current_params, recent_trades
                        )
                        
                        if ollama_optimization:
                            logger.info("Ollama AI provided optimization suggestions")
                            # Parse Ollama suggestions and convert to ParameterSuggestion format
                            suggestions = await self._parse_ollama_suggestions(
                                ollama_optimization, current_params
                            )
                            if suggestions:
                                return suggestions
                except Exception as e:
                    logger.warning(f"Ollama analysis failed, using fallback: {e}")
            
            # Fallback to traditional analysis
            suggestions = {}
            
            # RSI parameter optimization
            rsi_suggestion = await self._optimize_rsi_parameters(recent_trades)
            if rsi_suggestion:
                suggestions['rsi_period'] = rsi_suggestion
            
            # MACD parameter optimization
            macd_suggestion = await self._optimize_macd_parameters(recent_trades)
            if macd_suggestion:
                suggestions['macd_fast_period'] = macd_suggestion
            
            # Bollinger Bands optimization
            bb_suggestion = await self._optimize_bollinger_parameters(recent_trades)
            if bb_suggestion:
                suggestions['bollinger_std_dev'] = bb_suggestion
            
            # Risk management optimization
            risk_suggestion = await self._optimize_risk_parameters(recent_trades)
            if risk_suggestion:
                suggestions['risk_per_trade'] = risk_suggestion
            
            return suggestions if suggestions else None
        
        except Exception as e:
            logger.error(f"Error in AI performance analysis: {e}")
            return None

    async def suggest_config_from_research(self, research_summary: List[Dict]) -> Optional[Dict[str, ParameterSuggestion]]:
        """Suggest config updates based on pattern research results"""
        try:
            if not self.enabled or not research_summary:
                return None

            current_params = {
                'rsi_period': self.config['trading']['indicators']['rsi']['period'],
                'macd_fast': self.config['trading']['indicators']['macd']['fast_period'],
                'risk_per_trade': self.config['trading']['risk_per_trade'],
                'bollinger_std': self.config['trading']['indicators']['bollinger_bands']['std_dev'],
                'enable_rsi': self.config['trading']['indicators'].get('rsi', {}).get('enabled', True),
                'enable_macd': self.config['trading']['indicators'].get('macd', {}).get('enabled', True),
                'enable_bollinger_bands': self.config['trading']['indicators'].get('bollinger_bands', {}).get('enabled', True),
                'enable_ema': self.config['trading']['indicators'].get('ema', {}).get('enabled', True),
                'enable_vwap': self.config['trading']['indicators'].get('vwap', {}).get('enabled', True),
                'enable_stochastic': self.config['trading']['indicators'].get('stochastic', {}).get('enabled', False),
                'enable_williams_r': self.config['trading']['indicators'].get('williams_r', {}).get('enabled', False),
                'enable_cci': self.config['trading']['indicators'].get('cci', {}).get('enabled', False)
            }

            if self.use_ollama and self.ollama and self.ollama.is_available():
                prompt = (
                    "You are optimizing config parameters based on pattern research results.\n"
                    "Only suggest values for these parameters: rsi_period, macd_fast_period, "
                    "bollinger_std_dev, risk_per_trade, enable_rsi, enable_macd, "
                    "enable_bollinger_bands, enable_ema, enable_vwap, enable_stochastic, "
                    "enable_williams_r, enable_cci.\n"
                    "Respond with a short plain-text list of suggestions using parameter names "
                    "and numeric/true/false values (no JSON).\n\n"
                    f"Current params: {current_params}\n"
                    f"Research summary: {research_summary}\n"
                )
                response = self.ollama.generate(prompt, temperature=0.2, max_tokens=300)
                if response:
                    parsed = await self._parse_ollama_suggestions({"suggestions": response}, current_params)
                    if parsed:
                        return parsed

            return self._heuristic_research_suggestions(research_summary, current_params)
        except Exception as e:
            logger.error(f"Error generating research-based suggestions: {e}")
            return None

    def _heuristic_research_suggestions(
        self, research_summary: List[Dict], current_params: Dict
    ) -> Dict[str, ParameterSuggestion]:
        """Fallback suggestions based on simple research heuristics"""
        suggestions: Dict[str, ParameterSuggestion] = {}

        total_occ = sum(item.get("occurrences", 0) for item in research_summary) or 1
        weighted_success = sum(
            item.get("success_rate", 0) * item.get("occurrences", 0) for item in research_summary
        )
        avg_success = weighted_success / total_occ

        current_risk = float(current_params.get("risk_per_trade", 0.02))
        if avg_success < 0.45:
            new_risk = max(0.005, round(current_risk - 0.005, 4))
            if new_risk != current_risk:
                suggestions["risk_per_trade"] = ParameterSuggestion(
                    parameter="risk_per_trade",
                    current_value=current_risk,
                    suggested_value=new_risk,
                    confidence=0.6,
                    reason="Research success rate is low; reducing risk per trade",
                    expected_improvement=0.02
                )
        elif avg_success > 0.6:
            new_risk = min(0.03, round(current_risk + 0.005, 4))
            if new_risk != current_risk:
                suggestions["risk_per_trade"] = ParameterSuggestion(
                    parameter="risk_per_trade",
                    current_value=current_risk,
                    suggested_value=new_risk,
                    confidence=0.6,
                    reason="Research success rate is strong; modestly increasing risk per trade",
                    expected_improvement=0.02
                )

        ranked = sorted(
            research_summary,
            key=lambda item: item.get("success_rate", 0),
            reverse=True
        )
        top_patterns = [item.get("pattern_name") for item in ranked[:3]]
        reversal_patterns = {"double_bottom", "double_top", "hammer", "engulfing", "doji"}
        trend_patterns = {"higher_highs", "lower_lows"}

        if any(p in reversal_patterns for p in top_patterns):
            if not current_params.get("enable_stochastic", False):
                suggestions["enable_stochastic"] = ParameterSuggestion(
                    parameter="enable_stochastic",
                    current_value=False,
                    suggested_value=True,
                    confidence=0.55,
                    reason="Reversal patterns perform well; enable stochastic confirmation",
                    expected_improvement=0.01
                )
            elif not current_params.get("enable_williams_r", False):
                suggestions["enable_williams_r"] = ParameterSuggestion(
                    parameter="enable_williams_r",
                    current_value=False,
                    suggested_value=True,
                    confidence=0.55,
                    reason="Reversal patterns perform well; enable Williams %R confirmation",
                    expected_improvement=0.01
                )

        if any(p in trend_patterns for p in top_patterns):
            if not current_params.get("enable_ema", False):
                suggestions["enable_ema"] = ParameterSuggestion(
                    parameter="enable_ema",
                    current_value=False,
                    suggested_value=True,
                    confidence=0.55,
                    reason="Trend patterns perform well; enable EMA confirmation",
                    expected_improvement=0.01
                )
            elif not current_params.get("enable_vwap", False):
                suggestions["enable_vwap"] = ParameterSuggestion(
                    parameter="enable_vwap",
                    current_value=False,
                    suggested_value=True,
                    confidence=0.55,
                    reason="Trend patterns perform well; enable VWAP confirmation",
                    expected_improvement=0.01
                )

        return suggestions

    async def evaluate_trade_signal(self, signal, indicators: Dict) -> Dict[str, Any]:
        """Evaluate a trade signal for hard-gating approval"""
        min_confidence = self.trade_gating_config.get('min_confidence', 0.6)
        fail_open = self.trade_gating_config.get('fail_open', False)

        if not self.trade_gating_enabled or not self.enabled:
            return {"approve": True, "confidence": 1.0, "reason": "AI gating disabled"}

        # Use Ollama when available
        if self.use_ollama and self.ollama and self.ollama.is_available():
            try:
                async with self._gate_lock:
                    prompt = (
                        "Evaluate this trade signal and respond in JSON with keys "
                        "`approve` (true/false), `confidence` (0-1), and `reason`.\n\n"
                        f"Signal: action={signal.action}, confidence={signal.confidence:.2f}, "
                        f"entry={signal.entry_price:.6f}, stop={signal.stop_loss:.6f}, "
                        f"take_profit={signal.take_profit:.6f}\n"
                        f"Indicators: rsi={indicators.get('rsi', pd.Series()).iloc[-1] if isinstance(indicators.get('rsi'), pd.Series) else indicators.get('rsi')}, "
                        f"macd_hist={indicators.get('macd_histogram', pd.Series()).iloc[-1] if isinstance(indicators.get('macd_histogram'), pd.Series) else indicators.get('macd_histogram')}, "
                        f"bb_width={indicators.get('bb_width', pd.Series()).iloc[-1] if isinstance(indicators.get('bb_width'), pd.Series) else indicators.get('bb_width')}, "
                        f"ema_short={indicators.get('ema_short', pd.Series()).iloc[-1] if isinstance(indicators.get('ema_short'), pd.Series) else indicators.get('ema_short')}, "
                        f"ema_long={indicators.get('ema_long', pd.Series()).iloc[-1] if isinstance(indicators.get('ema_long'), pd.Series) else indicators.get('ema_long')}"
                    )
                    response = self.ollama.generate(prompt, temperature=0.2, max_tokens=150)
                    if response:
                        response = response.strip()
                        if response.startswith("{"):
                            data = json.loads(response)
                            approve = bool(data.get("approve", False))
                            confidence = float(data.get("confidence", 0))
                            reason = data.get("reason", "AI evaluation")
                            return {
                                "approve": approve and confidence >= min_confidence,
                                "confidence": confidence,
                                "reason": reason
                            }
                        # Fallback parsing if JSON is not returned
                        upper = response.upper()
                        approve = "APPROVE" in upper or "YES" in upper or "BUY" in upper
                        return {
                            "approve": approve and signal.confidence >= min_confidence,
                            "confidence": signal.confidence,
                            "reason": response[:200]
                        }
            except Exception as e:
                logger.warning(f"AI gating failed: {e}")

        # Fallback gating when AI is unavailable
        if fail_open:
            return {"approve": True, "confidence": signal.confidence, "reason": "AI unavailable, fail-open enabled"}

        # Hard-gate: reject if AI is unavailable and fail-open is disabled
        return {
            "approve": False,
            "confidence": 0.0,
            "reason": "AI unavailable, hard-gate rejection"
        }
    
    async def detect_patterns(self, df: pd.DataFrame, indicators: Dict, use_ai: bool = True) -> List[PatternMatch]:
        """Detect market patterns in current data
        Uses Ollama AI if available for enhanced pattern recognition"""
        try:
            if not self.enabled or df.empty:
                return []
            
            patterns = []
            
            # Try Ollama AI pattern detection first if available
            if use_ai and self.use_ollama and self.ollama and self.ollama.is_available():
                try:
                    # Prepare market data for Ollama
                    market_data = {
                        'current_price': float(df['close'].iloc[-1]),
                        'high_24h': float(df['high'].max()),
                        'low_24h': float(df['low'].min()),
                        'volume_24h': float(df['volume'].sum())
                    }
                    
                    # Prepare indicators for Ollama
                    indicators_for_ollama = {}
                    for key, value in indicators.items():
                        if isinstance(value, pd.Series) and len(value) > 0:
                            indicators_for_ollama[key] = {'value': float(value.iloc[-1])}
                        elif isinstance(value, (int, float)):
                            indicators_for_ollama[key] = value
                    
                    # Get AI pattern detection
                    ollama_patterns = self.ollama.detect_market_patterns(
                        market_data, indicators_for_ollama
                    )
                    
                    if ollama_patterns:
                        # Convert Ollama patterns to PatternMatch format
                        for pattern_data in ollama_patterns:
                            patterns.append(PatternMatch(
                                pattern_name=pattern_data.get('pattern', 'AI Pattern'),
                                confidence=pattern_data.get('confidence', 0.7),
                                historical_success_rate=0.65,  # Default
                                recommended_action=pattern_data.get('action', 'hold'),
                                risk_level='medium'
                            ))
                        logger.debug(f"Ollama detected {len(patterns)} patterns")
                except Exception as e:
                    logger.warning(f"Ollama pattern detection failed, using fallback: {e}")
            
            # Traditional pattern detection (always run as backup/confirmation)
            # Detect bullish divergence
            bullish_div = self._detect_bullish_divergence(df, indicators)
            if bullish_div:
                patterns.append(bullish_div)
            
            # Detect bearish divergence
            bearish_div = self._detect_bearish_divergence(df, indicators)
            if bearish_div:
                patterns.append(bearish_div)
            
            # Detect Bollinger Band squeeze
            bb_squeeze = self._detect_bollinger_squeeze(indicators)
            if bb_squeeze:
                patterns.append(bb_squeeze)
            
            # Detect MACD signals
            macd_signal = self._detect_macd_patterns(indicators)
            if macd_signal:
                patterns.append(macd_signal)
            
            # Detect volume patterns
            volume_pattern = self._detect_volume_patterns(df, indicators)
            if volume_pattern:
                patterns.append(volume_pattern)
            
            # Remove duplicates based on pattern name
            seen = set()
            unique_patterns = []
            for pattern in patterns:
                if pattern.pattern_name not in seen:
                    seen.add(pattern.pattern_name)
                    unique_patterns.append(pattern)
            
            return unique_patterns
        
        except Exception as e:
            logger.error(f"Error detecting patterns: {e}")
            return []

    def apply_research_summary(self, records: List[Dict]):
        """Update internal research stats from pattern research results"""
        try:
            if not records:
                return

            for record in records:
                key = f"{record.get('pattern_name')}:{record.get('timeframe')}"
                self.research_stats.setdefault(key, []).append(record)

            # Update known template success rates if matching names exist
            for template_name in self.pattern_templates.keys():
                matching = [r for r in records if r.get('pattern_name') == template_name]
                if not matching:
                    continue
                total_occ = sum(r.get('occurrences', 0) for r in matching) or 1
                weighted_success = sum(r.get('success_rate', 0) * r.get('occurrences', 0) for r in matching)
                self.pattern_templates[template_name]['success_rate'] = weighted_success / total_occ

            logger.info("Applied research summary to AI assistant")
        except Exception as e:
            logger.error(f"Error applying research summary: {e}")
    
    def _detect_bullish_divergence(self, df: pd.DataFrame, indicators: Dict) -> Optional[PatternMatch]:
        """Detect bullish divergence pattern"""
        try:
            if len(df) < 20:
                return None
            
            prices = df['close'].values[-20:]
            rsi_values = indicators.get('rsi', pd.Series()).values[-20:]
            
            if len(rsi_values) < 20:
                return None
            
            # Find recent lows
            price_lows = []
            rsi_lows = []
            
            for i in range(5, 15):
                if (prices[i] < prices[i-1] and prices[i] < prices[i+1] and
                    prices[i] < prices[i-2] and prices[i] < prices[i+2]):
                    price_lows.append((i, prices[i]))
                    rsi_lows.append((i, rsi_values[i]))
            
            if len(price_lows) >= 2:
                # Check for divergence
                latest_price_low = price_lows[-1][1]
                previous_price_low = price_lows[-2][1]
                latest_rsi_low = rsi_lows[-1][1]
                previous_rsi_low = rsi_lows[-2][1]
                
                if (latest_price_low < previous_price_low and 
                    latest_rsi_low > previous_rsi_low):
                    
                    confidence = min(0.9, abs(latest_rsi_low - previous_rsi_low) / 10)
                    
                    return PatternMatch(
                        pattern_name='bullish_divergence',
                        confidence=confidence,
                        historical_success_rate=self.pattern_templates['bullish_divergence']['success_rate'],
                        recommended_action='buy',
                        risk_level='medium'
                    )
            
            return None
        
        except Exception as e:
            logger.error(f"Error detecting bullish divergence: {e}")
            return None
    
    def _detect_bearish_divergence(self, df: pd.DataFrame, indicators: Dict) -> Optional[PatternMatch]:
        """Detect bearish divergence pattern"""
        try:
            if len(df) < 20:
                return None
            
            prices = df['close'].values[-20:]
            rsi_values = indicators.get('rsi', pd.Series()).values[-20:]
            
            if len(rsi_values) < 20:
                return None
            
            # Find recent highs
            price_highs = []
            rsi_highs = []
            
            for i in range(5, 15):
                if (prices[i] > prices[i-1] and prices[i] > prices[i+1] and
                    prices[i] > prices[i-2] and prices[i] > prices[i+2]):
                    price_highs.append((i, prices[i]))
                    rsi_highs.append((i, rsi_values[i]))
            
            if len(price_highs) >= 2:
                # Check for divergence
                latest_price_high = price_highs[-1][1]
                previous_price_high = price_highs[-2][1]
                latest_rsi_high = rsi_highs[-1][1]
                previous_rsi_high = rsi_highs[-2][1]
                
                if (latest_price_high > previous_price_high and 
                    latest_rsi_high < previous_rsi_high):
                    
                    confidence = min(0.9, abs(latest_rsi_high - previous_rsi_high) / 10)
                    
                    return PatternMatch(
                        pattern_name='bearish_divergence',
                        confidence=confidence,
                        historical_success_rate=self.pattern_templates['bearish_divergence']['success_rate'],
                        recommended_action='sell',
                        risk_level='medium'
                    )
            
            return None
        
        except Exception as e:
            logger.error(f"Error detecting bearish divergence: {e}")
            return None
    
    def _detect_bollinger_squeeze(self, indicators: Dict) -> Optional[PatternMatch]:
        """Detect Bollinger Band squeeze pattern"""
        try:
            bb_width = indicators.get('bb_width', pd.Series())
            if len(bb_width) < 20:
                return None
            
            current_width = bb_width.iloc[-1]
            avg_width = bb_width.rolling(20).mean().iloc[-1]
            
            # Squeeze detected when current width is significantly below average
            if current_width < avg_width * 0.7:
                confidence = min(0.9, (avg_width - current_width) / avg_width)
                
                return PatternMatch(
                    pattern_name='bollinger_squeeze',
                    confidence=confidence,
                    historical_success_rate=self.pattern_templates['bollinger_squeeze']['success_rate'],
                    recommended_action='wait_for_breakout',
                    risk_level='high'
                )
            
            return None
        
        except Exception as e:
            logger.error(f"Error detecting Bollinger squeeze: {e}")
            return None
    
    def _detect_macd_patterns(self, indicators: Dict) -> Optional[PatternMatch]:
        """Detect MACD pattern signals"""
        try:
            macd_line = indicators.get('macd_line', pd.Series())
            macd_signal = indicators.get('macd_signal', pd.Series())
            macd_histogram = indicators.get('macd_histogram', pd.Series())
            
            if len(macd_histogram) < 3:
                return None
            
            # Golden cross detection
            if (macd_line.iloc[-1] > macd_signal.iloc[-1] and 
                macd_line.iloc[-2] <= macd_signal.iloc[-2] and
                macd_histogram.iloc[-1] > 0):
                
                confidence = min(0.8, abs(macd_histogram.iloc[-1]) * 10)
                
                return PatternMatch(
                    pattern_name='macd_golden_cross',
                    confidence=confidence,
                    historical_success_rate=self.pattern_templates['macd_golden_cross']['success_rate'],
                    recommended_action='buy',
                    risk_level='low'
                )
            
            # Death cross detection
            elif (macd_line.iloc[-1] < macd_signal.iloc[-1] and 
                  macd_line.iloc[-2] >= macd_signal.iloc[-2] and
                  macd_histogram.iloc[-1] < 0):
                
                confidence = min(0.8, abs(macd_histogram.iloc[-1]) * 10)
                
                return PatternMatch(
                    pattern_name='macd_death_cross',
                    confidence=confidence,
                    historical_success_rate=0.55,  # Similar to golden cross
                    recommended_action='sell',
                    risk_level='low'
                )
            
            return None
        
        except Exception as e:
            logger.error(f"Error detecting MACD patterns: {e}")
            return None
    
    def _detect_volume_patterns(self, df: pd.DataFrame, indicators: Dict) -> Optional[PatternMatch]:
        """Detect volume-based patterns"""
        try:
            if len(df) < 10:
                return None
            
            volume = df['volume'].values[-10:]
            volume_sma = indicators.get('volume_sma', pd.Series())
            
            if len(volume_sma) < 1:
                return None
            
            current_volume = volume[-1]
            avg_volume = volume_sma.iloc[-1]
            
            # Volume spike detection
            if current_volume > avg_volume * 2:
                # Check price movement direction
                price_change = (df['close'].iloc[-1] - df['close'].iloc[-2]) / df['close'].iloc[-2]
                
                confidence = min(0.9, (current_volume / avg_volume - 1) / 2)
                action = 'buy' if price_change > 0 else 'sell'
                
                return PatternMatch(
                    pattern_name='volume_spike',
                    confidence=confidence,
                    historical_success_rate=self.pattern_templates['volume_spike']['success_rate'],
                    recommended_action=action,
                    risk_level='medium'
                )
            
            return None
        
        except Exception as e:
            logger.error(f"Error detecting volume patterns: {e}")
            return None
    
    async def _get_recent_trades(self) -> List[Dict]:
        """Get recent trade data for analysis"""
        try:
            # This would typically load from database
            # For now, return empty list as placeholder
            return []
        except Exception as e:
            logger.error(f"Error getting recent trades: {e}")
            return []
    
    async def _optimize_rsi_parameters(self, trades: List[Dict]) -> Optional[ParameterSuggestion]:
        """Optimize RSI parameters based on recent performance"""
        try:
            if len(trades) < 20:
                return None
            
            current_period = self.config['trading']['indicators']['rsi']['period']
            
            # Simulate different RSI periods
            periods_to_test = [3, 5, 7, 9, 12]
            best_period = current_period
            best_performance = 0
            
            for period in periods_to_test:
                # Calculate hypothetical performance with this period
                # This is a simplified simulation
                performance = self._simulate_rsi_performance(trades, period)
                if performance > best_performance:
                    best_performance = performance
                    best_period = period
            
            if best_period != current_period and best_performance > 0.1:
                return ParameterSuggestion(
                    parameter='rsi_period',
                    current_value=current_period,
                    suggested_value=best_period,
                    confidence=min(0.9, best_performance),
                    reason=f"Backtesting shows {best_performance*100:.1f}% better performance",
                    expected_improvement=best_performance
                )
            
            return None
        
        except Exception as e:
            logger.error(f"Error optimizing RSI parameters: {e}")
            return None
    
    def _simulate_rsi_performance(self, trades: List[Dict], period: int) -> float:
        """Simulate RSI performance with different period"""
        try:
            # Simplified simulation - would need actual backtesting
            # Return random performance for demonstration
            return np.random.uniform(0, 0.3)
        except Exception as e:
            logger.error(f"Error simulating RSI performance: {e}")
            return 0.0
    
    async def _optimize_macd_parameters(self, trades: List[Dict]) -> Optional[ParameterSuggestion]:
        """Optimize MACD parameters"""
        try:
            # Similar to RSI optimization but for MACD
            current_fast = self.config['trading']['indicators']['macd']['fast_period']
            
            # Test different fast periods
            fast_periods = [5, 6, 8, 10, 12]
            best_fast = current_fast
            best_performance = 0
            
            for fast in fast_periods:
                performance = self._simulate_macd_performance(trades, fast)
                if performance > best_performance:
                    best_performance = performance
                    best_fast = fast
            
            if best_fast != current_fast and best_performance > 0.1:
                return ParameterSuggestion(
                    parameter='macd_fast_period',
                    current_value=current_fast,
                    suggested_value=best_fast,
                    confidence=min(0.9, best_performance),
                    reason=f"Optimized MACD shows {best_performance*100:.1f}% improvement",
                    expected_improvement=best_performance
                )
            
            return None
        
        except Exception as e:
            logger.error(f"Error optimizing MACD parameters: {e}")
            return None
    
    def _simulate_macd_performance(self, trades: List[Dict], fast_period: int) -> float:
        """Simulate MACD performance"""
        try:
            return np.random.uniform(0, 0.25)
        except Exception as e:
            return 0.0
    
    async def _optimize_bollinger_parameters(self, trades: List[Dict]) -> Optional[ParameterSuggestion]:
        """Optimize Bollinger Bands parameters"""
        try:
            current_std = self.config['trading']['indicators']['bollinger_bands']['std_dev']
            
            # Test different standard deviations
            std_devs = [1.2, 1.5, 1.8, 2.0, 2.2]
            best_std = current_std
            best_performance = 0
            
            for std in std_devs:
                performance = self._simulate_bb_performance(trades, std)
                if performance > best_performance:
                    best_performance = performance
                    best_std = std
            
            if best_std != current_std and best_performance > 0.1:
                return ParameterSuggestion(
                    parameter='bollinger_std_dev',
                    current_value=current_std,
                    suggested_value=best_std,
                    confidence=min(0.9, best_performance),
                    reason=f"Optimized Bollinger Bands show {best_performance*100:.1f}% improvement",
                    expected_improvement=best_performance
                )
            
            return None
        
        except Exception as e:
            logger.error(f"Error optimizing Bollinger parameters: {e}")
            return None
    
    def _simulate_bb_performance(self, trades: List[Dict], std_dev: float) -> float:
        """Simulate Bollinger Bands performance"""
        try:
            return np.random.uniform(0, 0.2)
        except Exception as e:
            return 0.0
    
    async def _optimize_risk_parameters(self, trades: List[Dict]) -> Optional[ParameterSuggestion]:
        """Optimize risk management parameters"""
        try:
            current_risk = self.config['trading']['risk_per_trade']
            
            # Analyze recent trade performance
            if not trades:
                return None
            
            # Calculate win rate and average returns
            wins = sum(1 for trade in trades if trade.get('pnl', 0) > 0)
            win_rate = wins / len(trades)
            
            # Suggest risk adjustment based on performance
            if win_rate > 0.6:
                # High win rate - could increase risk slightly
                suggested_risk = min(0.025, current_risk * 1.1)
                reason = f"High win rate ({win_rate*100:.1f}%) suggests room for slight risk increase"
            elif win_rate < 0.4:
                # Low win rate - should decrease risk
                suggested_risk = max(0.01, current_risk * 0.9)
                reason = f"Low win rate ({win_rate*100:.1f}%) suggests risk reduction needed"
            else:
                return None
            
            if abs(suggested_risk - current_risk) > 0.002:
                return ParameterSuggestion(
                    parameter='risk_per_trade',
                    current_value=current_risk,
                    suggested_value=suggested_risk,
                    confidence=0.8,
                    reason=reason,
                    expected_improvement=0.1
                )
            
            return None
        
        except Exception as e:
            logger.error(f"Error optimizing risk parameters: {e}")
            return None
    
    def learn_from_trade(self, trade_data: Dict):
        """Learn from completed trade"""
        try:
            if not self.enabled:
                return
            
            # Store trade data for learning
            self.trade_history.append({
                'timestamp': datetime.now(),
                'symbol': trade_data.get('symbol'),
                'action': trade_data.get('action'),
                'entry_price': trade_data.get('entry_price'),
                'exit_price': trade_data.get('exit_price'),
                'pnl': trade_data.get('pnl'),
                'indicators': trade_data.get('indicators', {}),
                'patterns': trade_data.get('patterns', [])
            })
            
            # Update pattern success rates
            self._update_pattern_success_rates(trade_data)
            
            # Limit history size
            if len(self.trade_history) > 1000:
                self.trade_history = self.trade_history[-1000:]
        
        except Exception as e:
            logger.error(f"Error learning from trade: {e}")
    
    def _update_pattern_success_rates(self, trade_data: Dict):
        """Update pattern success rates based on trade outcome"""
        try:
            patterns = trade_data.get('patterns', [])
            pnl = trade_data.get('pnl', 0)
            
            for pattern in patterns:
                pattern_name = pattern.get('pattern_name')
                if pattern_name not in self.market_patterns:
                    self.market_patterns[pattern_name] = {
                        'total_trades': 0,
                        'successful_trades': 0,
                        'success_rate': 0.5
                    }
                
                self.market_patterns[pattern_name]['total_trades'] += 1
                if pnl > 0:
                    self.market_patterns[pattern_name]['successful_trades'] += 1
                
                # Update success rate
                total = self.market_patterns[pattern_name]['total_trades']
                successful = self.market_patterns[pattern_name]['successful_trades']
                self.market_patterns[pattern_name]['success_rate'] = successful / total
        
        except Exception as e:
            logger.error(f"Error updating pattern success rates: {e}")
    
    def get_pattern_confidence(self, pattern_name: str) -> float:
        """Get confidence level for a specific pattern"""
        try:
            if pattern_name in self.market_patterns:
                pattern_data = self.market_patterns[pattern_name]
                if pattern_data['total_trades'] >= 10:
                    return pattern_data['success_rate']
            
            # Return default from template
            return self.pattern_templates.get(pattern_name, {}).get('success_rate', 0.5)
        
        except Exception as e:
            logger.error(f"Error getting pattern confidence: {e}")
            return 0.5
    
    def save_learning_data(self, filepath: str):
        """Save learning data to file"""
        try:
            data = {
                'trade_history': self.trade_history,
                'market_patterns': self.market_patterns,
                'parameter_performance': self.parameter_performance
            }
            
            with open(filepath, 'wb') as f:
                pickle.dump(data, f)
            
            logger.info(f"Learning data saved to {filepath}")
        
        except Exception as e:
            logger.error(f"Error saving learning data: {e}")
    
    def load_learning_data(self, filepath: str):
        """Load learning data from file"""
        try:
            with open(filepath, 'rb') as f:
                data = pickle.load(f)
            
            self.trade_history = data.get('trade_history', [])
            self.market_patterns = data.get('market_patterns', {})
            self.parameter_performance = data.get('parameter_performance', {})
            
            logger.info(f"Learning data loaded from {filepath}")
        
        except Exception as e:
            logger.error(f"Error loading learning data: {e}")
    
    def _calculate_performance_metrics(self, trades: List[Dict]) -> Dict:
        """Calculate performance metrics from trade data"""
        try:
            if not trades:
                return {}
            
            total_trades = len(trades)
            winning_trades = sum(1 for t in trades if t.get('pnl', 0) > 0)
            losing_trades = total_trades - winning_trades
            
            gross_profit = sum(t.get('pnl', 0) for t in trades if t.get('pnl', 0) > 0)
            gross_loss = abs(sum(t.get('pnl', 0) for t in trades if t.get('pnl', 0) < 0))
            
            win_rate = winning_trades / total_trades if total_trades > 0 else 0
            profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
            
            net_pnl = sum(t.get('pnl', 0) for t in trades)
            
            # Calculate max drawdown
            cumulative_pnl = []
            running_total = 0
            for trade in trades:
                running_total += trade.get('pnl', 0)
                cumulative_pnl.append(running_total)
            
            if cumulative_pnl:
                peak = cumulative_pnl[0]
                max_drawdown = 0
                for value in cumulative_pnl:
                    if value > peak:
                        peak = value
                    drawdown = peak - value
                    if drawdown > max_drawdown:
                        max_drawdown = drawdown
            else:
                max_drawdown = 0
            
            return {
                'win_rate': win_rate,
                'total_trades': total_trades,
                'net_pnl': net_pnl,
                'profit_factor': profit_factor,
                'max_drawdown': max_drawdown,
                'gross_profit': gross_profit,
                'gross_loss': gross_loss
            }
        except Exception as e:
            logger.error(f"Error calculating performance metrics: {e}")
            return {}
    
    async def _parse_ollama_suggestions(self, ollama_optimization: Dict, 
                                       current_params: Dict) -> Dict[str, ParameterSuggestion]:
        """Parse Ollama optimization suggestions into ParameterSuggestion format"""
        try:
            suggestions = {}
            suggestions_text = ollama_optimization.get('suggestions', '')
            
            # Parse text suggestions (simple pattern matching)
            # In production, use more sophisticated parsing or structured output
            
            # Look for RSI suggestions
            if 'rsi' in suggestions_text.lower():
                # Try to extract suggested value
                import re
                rsi_match = re.search(r'rsi.*?(\d+)', suggestions_text.lower())
                if rsi_match:
                    suggested_rsi = int(rsi_match.group(1))
                    current_rsi = current_params.get('rsi_period', 14)
                    if suggested_rsi != current_rsi:
                        suggestions['rsi_period'] = ParameterSuggestion(
                            parameter='rsi_period',
                            current_value=current_rsi,
                            suggested_value=suggested_rsi,
                            confidence=0.75,
                            reason="Ollama AI optimization suggestion",
                            expected_improvement=0.05
                        )
            
            # Look for MACD suggestions
            if 'macd' in suggestions_text.lower():
                macd_match = re.search(r'macd.*?(\d+)', suggestions_text.lower())
                if macd_match:
                    suggested_macd = int(macd_match.group(1))
                    current_macd = current_params.get('macd_fast', 12)
                    if suggested_macd != current_macd:
                        suggestions['macd_fast_period'] = ParameterSuggestion(
                            parameter='macd_fast_period',
                            current_value=current_macd,
                            suggested_value=suggested_macd,
                            confidence=0.75,
                            reason="Ollama AI optimization suggestion",
                            expected_improvement=0.05
                        )
            
            # Look for risk suggestions
            if 'risk' in suggestions_text.lower():
                risk_match = re.search(r'risk.*?([\d.]+)', suggestions_text.lower())
                if risk_match:
                    suggested_risk = float(risk_match.group(1))
                    current_risk = current_params.get('risk_per_trade', 0.02)
                    if abs(suggested_risk - current_risk) > 0.001:
                        suggestions['risk_per_trade'] = ParameterSuggestion(
                            parameter='risk_per_trade',
                            current_value=current_risk,
                            suggested_value=suggested_risk,
                            confidence=0.75,
                            reason="Ollama AI optimization suggestion",
                            expected_improvement=0.05
                        )

            # Indicator enable/disable suggestions
            indicator_map = {
                "stochastic": "enable_stochastic",
                "williams": "enable_williams_r",
                "cci": "enable_cci",
                "rsi": "enable_rsi",
                "macd": "enable_macd",
                "bollinger": "enable_bollinger_bands",
                "ema": "enable_ema",
                "vwap": "enable_vwap"
            }
            lower_text = suggestions_text.lower()
            for key, param_name in indicator_map.items():
                if key in lower_text:
                    current_value = self.config.get('trading', {}).get('indicators', {}).get(
                        param_name.replace("enable_", ""),
                        {}
                    ).get('enabled', True if param_name in ["enable_rsi", "enable_macd", "enable_bollinger_bands", "enable_ema", "enable_vwap"] else False)
                    if "disable" in lower_text or "turn off" in lower_text:
                        suggestions[param_name] = ParameterSuggestion(
                            parameter=param_name,
                            current_value=current_value,
                            suggested_value=False,
                            confidence=0.7,
                            reason="Ollama AI suggests disabling indicator",
                            expected_improvement=0.03
                        )
                    elif "enable" in lower_text or "turn on" in lower_text or "include" in lower_text:
                        suggestions[param_name] = ParameterSuggestion(
                            parameter=param_name,
                            current_value=current_value,
                            suggested_value=True,
                            confidence=0.7,
                            reason="Ollama AI suggests enabling indicator",
                            expected_improvement=0.03
                        )
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error parsing Ollama suggestions: {e}")
            return {}