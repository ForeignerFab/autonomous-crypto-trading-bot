
"""
Risk Management Module
Implements comprehensive risk management and position sizing
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from loguru import logger
from datetime import datetime, timedelta


@dataclass
class RiskMetrics:
    """Risk metrics data structure"""
    max_position_size: float
    stop_loss_distance: float
    take_profit_distance: float
    risk_reward_ratio: float
    correlation_risk: float
    portfolio_heat: float


class RiskManager:
    """Comprehensive risk management system"""
    
    def __init__(self, config: Dict):
        """Initialize risk manager"""
        self.config = config
        self.risk_config = config['risk_management']
        self.trading_config = config['trading']
        
        # Risk tracking
        self.daily_trades = []
        self.daily_pnl = 0.0
        self.max_drawdown = 0.0
        self.peak_equity = config['trading']['initial_capital']
        
        logger.info("Risk manager initialized")
    
    def calculate_position_size(self, entry_price: float, stop_loss: float, max_risk: float) -> float:
        """Calculate position size based on risk management rules"""
        try:
            # Calculate risk per unit
            risk_per_unit = abs(entry_price - stop_loss)
            
            if risk_per_unit == 0:
                logger.warning("Risk per unit is zero, cannot calculate position size")
                return 0.0
            
            # Calculate position size based on fixed risk
            position_size = max_risk / risk_per_unit
            
            # Apply additional constraints
            max_position_value = self.peak_equity * 0.1  # Max 10% of equity per position
            max_size_by_value = max_position_value / entry_price
            
            position_size = min(position_size, max_size_by_value)
            
            logger.debug(f"Position size calculated: {position_size:.6f} (risk: £{max_risk}, price: {entry_price}, stop: {stop_loss})")
            return position_size
        
        except Exception as e:
            logger.error(f"Error calculating position size: {e}")
            return 0.0
    
    def calculate_kelly_criterion(self, win_rate: float, avg_win: float, avg_loss: float) -> float:
        """Calculate optimal position size using Kelly Criterion"""
        try:
            if avg_loss == 0 or win_rate == 0:
                return 0.0
            
            # Kelly formula: f = (bp - q) / b
            # where b = avg_win/avg_loss, p = win_rate, q = 1 - win_rate
            b = avg_win / abs(avg_loss)
            p = win_rate
            q = 1 - win_rate
            
            kelly_fraction = (b * p - q) / b
            
            # Apply Kelly fraction with safety margin (typically 25% of full Kelly)
            safe_kelly = max(0, min(kelly_fraction * 0.25, 0.1))  # Cap at 10%
            
            return safe_kelly
        
        except Exception as e:
            logger.error(f"Error calculating Kelly criterion: {e}")
            return 0.0
    
    async def validate_trade(self, signal) -> bool:
        """Validate if trade meets risk management criteria"""
        try:
            # Check basic risk parameters
            if signal.position_size <= 0:
                logger.warning("Invalid position size")
                return False
            
            # Check risk-reward ratio
            risk = abs(signal.entry_price - signal.stop_loss)
            reward = abs(signal.take_profit - signal.entry_price)
            
            if risk == 0:
                logger.warning("Zero risk detected")
                return False
            
            risk_reward_ratio = reward / risk
            min_rr_ratio = self.trading_config['strategy'].get('min_risk_reward_ratio', 1.5)
            
            if risk_reward_ratio < min_rr_ratio:
                logger.warning(f"Risk-reward ratio too low: {risk_reward_ratio:.2f} < {min_rr_ratio}")
                return False
            
            # Check correlation with existing positions
            if not await self._check_correlation_risk(signal.symbol):
                return False
            
            # Check portfolio heat
            if not self._check_portfolio_heat(signal):
                return False
            
            # Check volatility limits
            if not await self._check_volatility_limits(signal):
                return False
            
            return True
        
        except Exception as e:
            logger.error(f"Error validating trade: {e}")
            return False
    
    async def _check_correlation_risk(self, symbol: str) -> bool:
        """Check correlation risk with existing positions"""
        try:
            # This would require historical correlation analysis
            # For now, implement basic symbol similarity check
            
            # Get base asset from symbol (e.g., BTC from BTC-USDT)
            base_asset = symbol.split('-')[0] if '-' in symbol else symbol.replace('USDT', '')
            
            # Check if we already have positions in highly correlated assets
            correlated_assets = {
                'BTC': ['BTC', 'WBTC'],
                'ETH': ['ETH', 'WETH'],
                'BNB': ['BNB'],
                # Add more correlation groups as needed
            }
            
            # Simple correlation check - prevent multiple positions in same asset group
            for asset_group in correlated_assets.values():
                if base_asset in asset_group:
                    # Check existing positions for correlation
                    # This is a simplified implementation
                    return True
            
            return True
        
        except Exception as e:
            logger.error(f"Error checking correlation risk: {e}")
            return True  # Default to allowing trade if check fails
    
    def _check_portfolio_heat(self, signal) -> bool:
        """Check portfolio heat (total risk exposure)"""
        try:
            # Calculate current portfolio risk
            current_risk = signal.position_size * abs(signal.entry_price - signal.stop_loss)
            
            # Add to existing risk (simplified - would need actual position tracking)
            total_risk = current_risk
            
            # Check against maximum portfolio heat
            max_portfolio_risk = self.peak_equity * 0.06  # 6% max portfolio risk
            
            if total_risk > max_portfolio_risk:
                logger.warning(f"Portfolio heat too high: £{total_risk:.2f} > £{max_portfolio_risk:.2f}")
                return False
            
            return True
        
        except Exception as e:
            logger.error(f"Error checking portfolio heat: {e}")
            return True
    
    async def _check_volatility_limits(self, signal) -> bool:
        """Check if asset volatility is within acceptable limits"""
        try:
            # This would require recent volatility calculation
            # For now, implement basic checks
            
            # Check if stop loss is reasonable (not too tight or too wide)
            risk_percent = abs(signal.entry_price - signal.stop_loss) / signal.entry_price
            
            min_stop = float(self.risk_config.get('min_stop_loss_pct', 0.005))
            max_stop = float(self.risk_config.get('max_stop_loss_pct', 0.1))

            if risk_percent < min_stop:
                logger.warning(f"Stop loss too tight: {risk_percent*100:.2f}%")
                return False
            
            if risk_percent > max_stop:
                logger.warning(f"Stop loss too wide: {risk_percent*100:.2f}%")
                return False
            
            return True
        
        except Exception as e:
            logger.error(f"Error checking volatility limits: {e}")
            return True
    
    def update_daily_pnl(self, pnl: float):
        """Update daily P&L tracking"""
        try:
            self.daily_pnl += pnl
            
            # Update peak equity and drawdown
            current_equity = self.peak_equity + self.daily_pnl
            
            if current_equity > self.peak_equity:
                self.peak_equity = current_equity
                self.max_drawdown = 0.0
            else:
                drawdown = self.peak_equity - current_equity
                self.max_drawdown = max(self.max_drawdown, drawdown)
            
            # Check risk limits
            self._check_risk_limits()
        
        except Exception as e:
            logger.error(f"Error updating daily P&L: {e}")

    def update_initial_capital(self, capital: float):
        """Update peak equity based on live balance"""
        try:
            if capital and capital > 0:
                self.peak_equity = float(capital)
                logger.info(f"Updated peak equity from live balance: {self.peak_equity:.2f}")
        except Exception as e:
            logger.error(f"Error updating initial capital: {e}")
    
    def _check_risk_limits(self):
        """Check if risk limits have been breached"""
        try:
            # Check daily loss limit
            if self.daily_pnl <= -self.risk_config['max_daily_loss']:
                logger.warning(f"Daily loss limit breached: £{self.daily_pnl:.2f}")
                return False
            
            # Check maximum drawdown
            if self.max_drawdown >= self.risk_config['max_drawdown']:
                logger.warning(f"Maximum drawdown breached: £{self.max_drawdown:.2f}")
                return False
            
            return True
        
        except Exception as e:
            logger.error(f"Error checking risk limits: {e}")
            return True
    
    def calculate_risk_metrics(self, positions: List) -> RiskMetrics:
        """Calculate comprehensive risk metrics"""
        try:
            if not positions:
                return RiskMetrics(0, 0, 0, 0, 0, 0)
            
            # Calculate portfolio-level metrics
            total_risk = sum(pos.size * abs(pos.entry_price - pos.stop_loss) for pos in positions)
            total_reward = sum(pos.size * abs(pos.take_profit - pos.entry_price) for pos in positions)
            
            avg_risk_reward = total_reward / total_risk if total_risk > 0 else 0
            portfolio_heat = total_risk / self.peak_equity
            
            # Calculate position size metrics
            position_sizes = [pos.size * pos.entry_price for pos in positions]
            max_position_size = max(position_sizes) if position_sizes else 0
            
            return RiskMetrics(
                max_position_size=max_position_size,
                stop_loss_distance=total_risk / len(positions) if positions else 0,
                take_profit_distance=total_reward / len(positions) if positions else 0,
                risk_reward_ratio=avg_risk_reward,
                correlation_risk=0.0,  # Would need correlation calculation
                portfolio_heat=portfolio_heat
            )
        
        except Exception as e:
            logger.error(f"Error calculating risk metrics: {e}")
            return RiskMetrics(0, 0, 0, 0, 0, 0)
    
    def get_position_sizing_recommendation(self, symbol: str, entry_price: float, 
                                         stop_loss: float, confidence: float) -> Dict:
        """Get position sizing recommendation based on multiple methods"""
        try:
            max_risk = self.trading_config['max_risk_amount']
            
            # Fixed risk method
            fixed_risk_size = self.calculate_position_size(entry_price, stop_loss, max_risk)
            
            # Confidence-adjusted sizing
            confidence_adjusted_size = fixed_risk_size * confidence
            
            # Kelly criterion (if we have historical data)
            kelly_size = fixed_risk_size * 0.5  # Placeholder - would need actual win/loss data
            
            # Conservative approach - take minimum
            recommended_size = min(fixed_risk_size, confidence_adjusted_size, kelly_size)
            
            return {
                'recommended_size': recommended_size,
                'fixed_risk_size': fixed_risk_size,
                'confidence_adjusted_size': confidence_adjusted_size,
                'kelly_size': kelly_size,
                'risk_amount': recommended_size * abs(entry_price - stop_loss),
                'position_value': recommended_size * entry_price
            }
        
        except Exception as e:
            logger.error(f"Error getting position sizing recommendation: {e}")
            return {'recommended_size': 0}
    
    def should_reduce_risk(self) -> bool:
        """Determine if risk should be reduced based on recent performance"""
        try:
            # Check recent performance
            if self.daily_pnl < -self.risk_config['max_daily_loss'] * 0.5:
                return True
            
            # Check drawdown
            if self.max_drawdown > self.risk_config['max_drawdown'] * 0.5:
                return True
            
            # Check consecutive losses (would need trade history)
            return False
        
        except Exception as e:
            logger.error(f"Error checking if should reduce risk: {e}")
            return False
    
    def get_emergency_stop_level(self) -> float:
        """Get emergency stop loss level"""
        try:
            emergency_level = self.peak_equity * (1 - self.risk_config.get('emergency_stop_loss', 0.15))
            return emergency_level
        except Exception as e:
            logger.error(f"Error calculating emergency stop level: {e}")
            return self.peak_equity * 0.85
