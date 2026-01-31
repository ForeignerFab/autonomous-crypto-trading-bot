"""
Ollama AI Service Integration
Provides free, powerful AI capabilities for trading analysis
"""

import requests
import json
from typing import Dict, List, Optional, Any
from loguru import logger
import os
from datetime import datetime


class OllamaService:
    """Service wrapper for Ollama AI integration"""
    
    def __init__(self, base_url: str = None, model: str = "llama3.2:7b"):
        """
        Initialize Ollama service
        
        Args:
            base_url: Ollama API base URL (default: http://localhost:11434)
            model: Model to use (default: llama3.2:7b)
        """
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = model or os.getenv("OLLAMA_MODEL", "llama3.2:7b")
        self.available = False
        try:
            self.timeout = float(os.getenv("OLLAMA_TIMEOUT", "90"))
        except ValueError:
            self.timeout = 90
        self._check_availability()
    
    def _check_availability(self) -> bool:
        """Check if Ollama is available"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            if response.status_code == 200:
                self.available = True
                logger.info(f"Ollama service available at {self.base_url}")
                return True
        except Exception as e:
            logger.warning(f"Ollama not available: {e}. AI features will use fallback methods.")
            self.available = False
            return False
        return False
    
    def is_available(self) -> bool:
        """Check if Ollama service is available"""
        return self.available
    
    def generate(self, prompt: str, system_prompt: str = None, temperature: float = 0.7, 
                 max_tokens: int = 1000) -> Optional[str]:
        """
        Generate text using Ollama
        
        Args:
            prompt: User prompt
            system_prompt: System prompt for context
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text or None if failed
        """
        if not self.available:
            return None
        
        try:
            # Combine system and user prompts
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens
                    }
                },
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
            else:
                logger.error(f"Ollama API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error calling Ollama: {e}")
            return None
    
    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> Optional[str]:
        """
        Chat with Ollama using message format
        
        Args:
            messages: List of messages in format [{"role": "user", "content": "..."}]
            temperature: Sampling temperature
            
        Returns:
            Assistant response or None
        """
        if not self.available:
            return None
        
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": temperature
                    }
                },
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('message', {}).get('content', '').strip()
            else:
                logger.error(f"Ollama chat error: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error in Ollama chat: {e}")
            return None
    
    def analyze_trading_performance(self, trade_data: List[Dict], 
                                   performance_metrics: Dict) -> Optional[Dict]:
        """
        Analyze trading performance using AI
        
        Args:
            trade_data: List of trade records
            performance_metrics: Performance metrics dictionary
            
        Returns:
            Analysis results or None
        """
        if not self.available:
            return None
        
        system_prompt = """You are an expert quantitative trading analyst. Analyze trading performance 
and provide actionable insights. Focus on:
1. Identifying patterns in winning vs losing trades
2. Suggesting parameter optimizations
3. Detecting market regime changes
4. Recommending risk adjustments

Provide responses in JSON format when possible."""
        
        prompt = f"""Analyze this trading performance data:

Performance Metrics:
- Win Rate: {performance_metrics.get('win_rate', 0):.2%}
- Total Trades: {performance_metrics.get('total_trades', 0)}
- Net P&L: {performance_metrics.get('net_pnl', 0):.2f}
- Profit Factor: {performance_metrics.get('profit_factor', 0):.2f}
- Max Drawdown: {performance_metrics.get('max_drawdown', 0):.2f}

Recent Trades: {len(trade_data)} trades

Provide:
1. Key insights about performance
2. Suggested parameter adjustments
3. Risk management recommendations
4. Market condition assessment"""
        
        response = self.generate(prompt, system_prompt, temperature=0.3)
        
        if response:
            try:
                # Try to parse as JSON if possible
                if response.startswith('{'):
                    return json.loads(response)
                else:
                    # Return as structured text
                    return {
                        'analysis': response,
                        'timestamp': datetime.now().isoformat()
                    }
            except:
                return {
                    'analysis': response,
                    'timestamp': datetime.now().isoformat()
                }
        
        return None
    
    def detect_market_patterns(self, market_data: Dict, indicators: Dict) -> Optional[List[Dict]]:
        """
        Detect market patterns using AI
        
        Args:
            market_data: Market data dictionary
            indicators: Technical indicators dictionary
            
        Returns:
            List of detected patterns or None
        """
        if not self.available:
            return None
        
        system_prompt = """You are an expert technical analyst. Identify market patterns and provide 
trading signals. Focus on:
1. Chart patterns (head and shoulders, triangles, etc.)
2. Candlestick patterns
3. Divergences
4. Support/resistance levels
5. Trend analysis

Provide structured analysis with confidence levels."""
        
        prompt = f"""Analyze this market data and identify patterns:

Price Data:
- Current Price: {market_data.get('current_price', 'N/A')}
- 24h High: {market_data.get('high_24h', 'N/A')}
- 24h Low: {market_data.get('low_24h', 'N/A')}
- Volume: {market_data.get('volume_24h', 'N/A')}

Technical Indicators:
- RSI: {indicators.get('rsi', {}).get('value', 'N/A') if isinstance(indicators.get('rsi'), dict) else indicators.get('rsi', 'N/A')}
- MACD: {indicators.get('macd', 'N/A')}
- Bollinger Bands: Upper={indicators.get('bb_upper', 'N/A')}, Lower={indicators.get('bb_lower', 'N/A')}

Identify:
1. Chart patterns present
2. Trading signals (BUY/SELL/HOLD)
3. Confidence level (0-100%)
4. Risk assessment
5. Recommended action"""
        
        response = self.generate(prompt, system_prompt, temperature=0.4)
        
        if response:
            # Parse response to extract patterns
            patterns = []
            # Simple parsing - in production, use more sophisticated parsing
            if 'BUY' in response.upper() or 'BULLISH' in response.upper():
                patterns.append({
                    'pattern': 'Bullish Signal',
                    'confidence': 0.7,
                    'action': 'buy',
                    'reasoning': response[:200]
                })
            elif 'SELL' in response.upper() or 'BEARISH' in response.upper():
                patterns.append({
                    'pattern': 'Bearish Signal',
                    'confidence': 0.7,
                    'action': 'sell',
                    'reasoning': response[:200]
                })
            
            return patterns if patterns else None
        
        return None
    
    def optimize_parameters(self, current_params: Dict, performance_history: List[Dict]) -> Optional[Dict]:
        """
        Optimize trading parameters using AI
        
        Args:
            current_params: Current parameter values
            performance_history: Historical performance data
            
        Returns:
            Optimization suggestions or None
        """
        if not self.available:
            return None
        
        system_prompt = """You are a quantitative trading optimization expert. Analyze parameter 
performance and suggest improvements. Consider:
1. Risk-reward ratios
2. Win rates
3. Drawdowns
4. Market conditions
5. Parameter interactions

Provide specific, actionable recommendations."""
        
        prompt = f"""Optimize these trading parameters based on performance:

Current Parameters:
{json.dumps(current_params, indent=2)}

Performance History:
- Total Trades: {len(performance_history)}
- Average Win Rate: {sum(p.get('win', 0) for p in performance_history) / len(performance_history) if performance_history else 0:.2%}
- Average P&L: {sum(p.get('pnl', 0) for p in performance_history) / len(performance_history) if performance_history else 0:.2f}

Suggest:
1. Parameter adjustments with reasoning
2. Expected impact on performance
3. Risk considerations
4. Implementation priority"""
        
        response = self.generate(prompt, system_prompt, temperature=0.3)
        
        if response:
            return {
                'suggestions': response,
                'timestamp': datetime.now().isoformat(),
                'current_params': current_params
            }
        
        return None
    
    def get_available_models(self) -> List[str]:
        """Get list of available Ollama models"""
        if not self.available:
            return []
        
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return [model['name'] for model in data.get('models', [])]
        except Exception as e:
            logger.error(f"Error getting models: {e}")
        
        return []
    
    def pull_model(self, model_name: str) -> bool:
        """Pull/download an Ollama model"""
        if not self.available:
            return False
        
        try:
            response = requests.post(
                f"{self.base_url}/api/pull",
                json={"name": model_name},
                stream=True,
                timeout=300
            )
            
            if response.status_code == 200:
                logger.info(f"Model {model_name} pulled successfully")
                return True
            else:
                logger.error(f"Failed to pull model: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Error pulling model: {e}")
            return False








