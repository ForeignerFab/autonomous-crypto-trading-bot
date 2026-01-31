
"""
OKX Autonomous Trading Bot
A comprehensive high-frequency cryptocurrency trading system
"""

__version__ = "1.0.0"
__author__ = "Autonomous Trading Systems"
__description__ = "High-frequency cryptocurrency trading bot for OKX with AI-enhanced decision making"

# Core modules
from .engine import TradingEngine
from .indicators import TechnicalIndicators
from .risk import RiskManager
from .okx_client import OKXClient
from .discord_bot import DiscordNotifier
from .ai_assistant import AIAssistant
from .reporter import ReportGenerator

__all__ = [
    "TradingEngine",
    "TechnicalIndicators", 
    "RiskManager",
    "OKXClient",
    "DiscordNotifier",
    "AIAssistant",
    "ReportGenerator"
]
