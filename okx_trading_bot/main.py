
"""
Main Entry Point for OKX Trading Bot
Orchestrates all components and handles startup/shutdown
"""

import asyncio
import signal
import sys
import os
from pathlib import Path
from loguru import logger
from datetime import datetime
import yaml
from dotenv import load_dotenv

# Add src directory to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.engine import TradingEngine
from src.discord_bot import DiscordNotifier
from src.database import DatabaseManager


class TradingBotManager:
    """Main trading bot manager"""
    
    def __init__(self, config_path: str = "config.yml"):
        """Initialize trading bot manager"""
        self.config_path = config_path
        self.config = None
        self.engine = None
        self.running = False
        
        # Setup logging
        self._setup_logging()
        
        # Load environment variables
        load_dotenv()
        
        logger.info("Trading Bot Manager initialized")
    
    def _setup_logging(self):
        """Setup logging configuration"""
        # Remove default logger
        logger.remove()
        
        # Add console logger
        logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level="INFO"
        )
        
        # Add file logger
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        
        logger.add(
            f"{log_dir}/trading_bot.log",
            rotation="10 MB",
            retention="30 days",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level="DEBUG"
        )
        
        # Add error file logger
        logger.add(
            f"{log_dir}/errors.log",
            rotation="10 MB",
            retention="90 days",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level="ERROR"
        )
    
    def _load_config(self) -> dict:
        """Load configuration from file"""
        try:
            if not os.path.exists(self.config_path):
                logger.error(f"Configuration file not found: {self.config_path}")
                logger.info("Please copy config_template.yml to config.yml and configure your settings")
                sys.exit(1)
            
            with open(self.config_path, 'r') as file:
                config = yaml.safe_load(file)
            
            # Load environment variables into config
            self._load_env_variables(config)
            
            logger.info(f"Configuration loaded from {self.config_path}")
            return config
        
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            sys.exit(1)
    
    def _load_env_variables(self, config: dict):
        """Load environment variables into configuration"""
        try:
            # OKX API credentials
            if 'okx' in config:
                config['okx']['api_key'] = os.getenv('OKX_API_KEY', config['okx'].get('api_key', ''))
                config['okx']['secret_key'] = os.getenv('OKX_SECRET_KEY', config['okx'].get('secret_key', ''))
                config['okx']['passphrase'] = os.getenv('OKX_PASSPHRASE', config['okx'].get('passphrase', ''))
            
            # Discord configuration
            if 'discord' in config:
                config['discord']['bot_token'] = os.getenv('DISCORD_BOT_TOKEN', config['discord'].get('bot_token', ''))
                config['discord']['channel_id'] = os.getenv('DISCORD_CHANNEL_ID', config['discord'].get('channel_id', ''))
                config['discord']['webhook_url'] = os.getenv('DISCORD_WEBHOOK_URL', config['discord'].get('webhook_url', ''))
            
            # Validate required credentials
            self._validate_credentials(config)
        
        except Exception as e:
            logger.error(f"Error loading environment variables: {e}")
            sys.exit(1)
    
    def _validate_credentials(self, config: dict):
        """Validate required credentials"""
        required_okx = ['api_key', 'secret_key', 'passphrase']
        missing_okx = [key for key in required_okx if not config.get('okx', {}).get(key)]
        
        if missing_okx:
            logger.error(f"Missing OKX credentials: {missing_okx}")
            logger.info("Please set the following environment variables:")
            for key in missing_okx:
                logger.info(f"  OKX_{key.upper()}")
            sys.exit(1)
        
        # Discord is optional but warn if not configured
        if not config.get('discord', {}).get('bot_token'):
            logger.warning("Discord bot token not configured - notifications will be disabled")
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating graceful shutdown...")
            self.running = False
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        if hasattr(signal, 'SIGHUP'):
            signal.signal(signal.SIGHUP, signal_handler)
    
    async def start(self):
        """Start the trading bot"""
        try:
            logger.info("=" * 60)
            logger.info("🚀 STARTING OKX AUTONOMOUS TRADING BOT")
            logger.info("=" * 60)
            
            # Load configuration
            self.config = self._load_config()
            
            # Setup signal handlers
            self._setup_signal_handlers()
            
            # Display configuration summary
            self._display_config_summary()
            
            # Initialize trading engine
            logger.info("Initializing trading engine...")
            self.engine = TradingEngine(self.config_path)
            
            # Start the engine
            self.running = True
            logger.info("Starting trading engine...")
            
            # Run the trading engine
            await self.engine.start()
        
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        except Exception as e:
            logger.error(f"Fatal error in trading bot: {e}")
            raise
        finally:
            await self.shutdown()
    
    def _display_config_summary(self):
        """Display configuration summary"""
        logger.info("Configuration Summary:")
        logger.info(f"  Initial Capital: £{self.config['trading']['initial_capital']}")
        logger.info(f"  Risk per Trade: {self.config['trading']['risk_per_trade']*100}%")
        logger.info(f"  Max Risk Amount: £{self.config['trading']['max_risk_amount']}")
        logger.info(f"  Max Active Pairs: {self.config['trading']['max_active_pairs']}")
        logger.info(f"  Timeframe: {self.config['trading']['strategy']['timeframe']}")
        logger.info(f"  Sandbox Mode: {self.config['okx']['sandbox']}")
        logger.info(f"  Discord Notifications: {'Enabled' if self.config['discord'].get('bot_token') else 'Disabled'}")
        logger.info(f"  AI Assistant: {'Enabled' if self.config['ai_assistant']['enabled'] else 'Disabled'}")
    
    async def shutdown(self):
        """Graceful shutdown"""
        try:
            logger.info("Initiating graceful shutdown...")
            
            if self.engine:
                await self.engine.stop()
            
            logger.info("Trading bot shutdown complete")
            logger.info("=" * 60)
        
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")


async def main():
    """Main entry point"""
    try:
        # Check for config file
        config_path = "config.yml"
        if not os.path.exists(config_path):
            print("❌ Configuration file 'config.yml' not found!")
            print("📋 Please copy 'config_template.yml' to 'config.yml' and configure your settings.")
            print("🔑 Don't forget to set up your .env file with API keys!")
            sys.exit(1)
        
        # Check for .env file
        if not os.path.exists('.env'):
            print("⚠️  Environment file '.env' not found!")
            print("📋 Please copy '.env.example' to '.env' and add your API keys.")
            print("🔑 Required: OKX_API_KEY, OKX_SECRET_KEY, OKX_PASSPHRASE")
            print("🤖 Optional: DISCORD_BOT_TOKEN, DISCORD_CHANNEL_ID, DISCORD_WEBHOOK_URL")
            sys.exit(1)
        
        # Create and start bot manager
        bot_manager = TradingBotManager(config_path)
        await bot_manager.start()
    
    except Exception as e:
        logger.error(f"Failed to start trading bot: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    
    # Run the bot
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Trading bot stopped by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)
