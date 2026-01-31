
"""
Database Management Module
Handles data storage, retrieval, and management for the trading bot
"""

import sqlite3
import aiosqlite
import pandas as pd
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from loguru import logger
import os
from dataclasses import asdict


class DatabaseManager:
    """SQLite database manager for trading bot data"""
    
    def __init__(self, config: Dict):
        """Initialize database manager"""
        self.config = config
        self.db_path = config.get('database', {}).get('path', 'data/trading_bot.db')
        self.backup_interval = config.get('database', {}).get('backup_interval', 3600)
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        logger.info(f"Database manager initialized: {self.db_path}")
    
    async def initialize(self):
        """Initialize database tables"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Create tables
                await self._create_tables(db)
                await db.commit()
            
            logger.info("Database initialized successfully")
        
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    async def _create_tables(self, db: aiosqlite.Connection):
        """Create database tables"""
        
        # Trades table
        await db.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                entry_price REAL NOT NULL,
                exit_price REAL,
                quantity REAL NOT NULL,
                pnl REAL,
                commission REAL DEFAULT 0,
                stop_loss REAL,
                take_profit REAL,
                entry_reason TEXT,
                exit_reason TEXT,
                indicators TEXT,
                patterns TEXT,
                confidence REAL,
                status TEXT DEFAULT 'open',
                order_id TEXT,
                exit_order_id TEXT
            )
        ''')
        
        # Account balance history
        await db.execute('''
            CREATE TABLE IF NOT EXISTS balance_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                total_balance REAL NOT NULL,
                available_balance REAL NOT NULL,
                unrealized_pnl REAL DEFAULT 0,
                realized_pnl REAL DEFAULT 0,
                equity REAL NOT NULL
            )
        ''')
        
        # Performance metrics
        await db.execute('''
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL UNIQUE,
                total_trades INTEGER DEFAULT 0,
                winning_trades INTEGER DEFAULT 0,
                losing_trades INTEGER DEFAULT 0,
                gross_profit REAL DEFAULT 0,
                gross_loss REAL DEFAULT 0,
                net_profit REAL DEFAULT 0,
                profit_factor REAL DEFAULT 0,
                sharpe_ratio REAL DEFAULT 0,
                max_drawdown REAL DEFAULT 0,
                win_rate REAL DEFAULT 0,
                avg_win REAL DEFAULT 0,
                avg_loss REAL DEFAULT 0,
                largest_win REAL DEFAULT 0,
                largest_loss REAL DEFAULT 0
            )
        ''')
        
        # Trading pairs performance
        await db.execute('''
            CREATE TABLE IF NOT EXISTS pair_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                date DATE NOT NULL,
                trades_count INTEGER DEFAULT 0,
                total_pnl REAL DEFAULT 0,
                win_rate REAL DEFAULT 0,
                avg_trade_duration INTEGER DEFAULT 0,
                volatility REAL DEFAULT 0,
                volume REAL DEFAULT 0,
                UNIQUE(symbol, date)
            )
        ''')
        
        # Market data cache
        await db.execute('''
            CREATE TABLE IF NOT EXISTS market_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                timeframe TEXT NOT NULL,
                open_price REAL NOT NULL,
                high_price REAL NOT NULL,
                low_price REAL NOT NULL,
                close_price REAL NOT NULL,
                volume REAL NOT NULL,
                UNIQUE(symbol, timestamp, timeframe)
            )
        ''')
        
        # AI learning data
        await db.execute('''
            CREATE TABLE IF NOT EXISTS ai_learning (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                pattern_name TEXT NOT NULL,
                success BOOLEAN NOT NULL,
                confidence REAL NOT NULL,
                market_conditions TEXT,
                parameters TEXT
            )
        ''')
        
        # System logs
        await db.execute('''
            CREATE TABLE IF NOT EXISTS system_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                level TEXT NOT NULL,
                module TEXT NOT NULL,
                message TEXT NOT NULL,
                details TEXT
            )
        ''')
        
        # Configuration history
        await db.execute('''
            CREATE TABLE IF NOT EXISTS config_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                parameter_name TEXT NOT NULL,
                old_value TEXT,
                new_value TEXT NOT NULL,
                reason TEXT,
                approved_by TEXT DEFAULT 'system'
            )
        ''')

        # Pattern research results
        await db.execute('''
            CREATE TABLE IF NOT EXISTS pattern_research (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                symbol TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                pattern_name TEXT NOT NULL,
                occurrences INTEGER DEFAULT 0,
                success_rate REAL DEFAULT 0,
                avg_return REAL DEFAULT 0,
                sample_size INTEGER DEFAULT 0
            )
        ''')
        
        # Create indexes for better performance
        await db.execute('CREATE INDEX IF NOT EXISTS idx_trades_timestamp ON trades(timestamp)')
        await db.execute('CREATE INDEX IF NOT EXISTS idx_trades_symbol ON trades(symbol)')
        await db.execute('CREATE INDEX IF NOT EXISTS idx_balance_timestamp ON balance_history(timestamp)')
        await db.execute('CREATE INDEX IF NOT EXISTS idx_performance_date ON performance_metrics(date)')
        await db.execute('CREATE INDEX IF NOT EXISTS idx_market_data_symbol_time ON market_data(symbol, timestamp)')
        await db.execute('CREATE INDEX IF NOT EXISTS idx_pattern_research_symbol_time ON pattern_research(symbol, timeframe)')
    
    async def close(self):
        """Close database connections"""
        logger.info("Database connections closed")

    async def get_recent_pattern_research(self, hours: int = 72, limit: int = 2000) -> List[Dict]:
        """Fetch recent pattern research records"""
        try:
            cutoff = datetime.now() - timedelta(hours=hours)
            cutoff_str = cutoff.strftime("%Y-%m-%d %H:%M:%S")
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute(
                    '''
                    SELECT pattern_name, timeframe, occurrences, success_rate, avg_return, sample_size, timestamp
                    FROM pattern_research
                    WHERE timestamp >= ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                    ''',
                    (cutoff_str, limit)
                )
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error fetching recent pattern research: {e}")
            return []
    
    async def log_trade(self, signal, order: Dict):
        """Log a new trade"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    INSERT INTO trades (
                        symbol, side, entry_price, quantity, stop_loss, take_profit,
                        entry_reason, indicators, patterns, confidence, order_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    signal.symbol,
                    signal.action,
                    signal.entry_price,
                    signal.position_size,
                    signal.stop_loss,
                    signal.take_profit,
                    signal.reasoning,
                    json.dumps(signal.indicators) if hasattr(signal, 'indicators') else None,
                    json.dumps([]) if not hasattr(signal, 'patterns') else json.dumps(signal.patterns),
                    signal.confidence,
                    order.get('id')
                ))
                await db.commit()
            
            logger.debug(f"Trade logged: {signal.symbol} {signal.action}")
        
        except Exception as e:
            logger.error(f"Error logging trade: {e}")
    
    async def log_trade_close(self, position, order: Dict, reason: str):
        """Log trade closure"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    UPDATE trades 
                    SET exit_price = ?, pnl = ?, exit_reason = ?, status = 'closed', exit_order_id = ?
                    WHERE symbol = ? AND status = 'open'
                ''', (
                    position.current_price,
                    position.pnl,
                    reason,
                    order.get('id'),
                    position.symbol
                ))
                await db.commit()
            
            logger.debug(f"Trade close logged: {position.symbol} P&L: £{position.pnl:.2f}")
        
        except Exception as e:
            logger.error(f"Error logging trade close: {e}")

    async def save_pattern_research(self, records: List[Dict]):
        """Save pattern research results"""
        try:
            if not records:
                return
            async with aiosqlite.connect(self.db_path) as db:
                await db.executemany('''
                    INSERT INTO pattern_research (
                        symbol, timeframe, pattern_name, occurrences,
                        success_rate, avg_return, sample_size
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', [
                    (
                        record.get('symbol'),
                        record.get('timeframe'),
                        record.get('pattern_name'),
                        record.get('occurrences', 0),
                        record.get('success_rate', 0.0),
                        record.get('avg_return', 0.0),
                        record.get('sample_size', 0)
                    )
                    for record in records
                ])
                await db.commit()
            logger.info(f"Saved {len(records)} pattern research rows")
        except Exception as e:
            logger.error(f"Error saving pattern research: {e}")
    
    async def log_balance(self, balance_data: Dict):
        """Log account balance"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    INSERT INTO balance_history (
                        total_balance, available_balance, unrealized_pnl, realized_pnl, equity
                    ) VALUES (?, ?, ?, ?, ?)
                ''', (
                    balance_data.get('total_balance', 0),
                    balance_data.get('available_balance', 0),
                    balance_data.get('unrealized_pnl', 0),
                    balance_data.get('realized_pnl', 0),
                    balance_data.get('equity', 0)
                ))
                await db.commit()
        
        except Exception as e:
            logger.error(f"Error logging balance: {e}")
    
    async def get_trades(self, symbol: Optional[str] = None, 
                        start_date: Optional[datetime] = None,
                        end_date: Optional[datetime] = None,
                        status: Optional[str] = None) -> List[Dict]:
        """Get trades with optional filters"""
        try:
            query = "SELECT * FROM trades WHERE 1=1"
            params = []
            
            if symbol:
                query += " AND symbol = ?"
                params.append(symbol)
            
            if start_date:
                query += " AND timestamp >= ?"
                params.append(start_date.isoformat())
            
            if end_date:
                query += " AND timestamp <= ?"
                params.append(end_date.isoformat())
            
            if status:
                query += " AND status = ?"
                params.append(status)
            
            query += " ORDER BY timestamp DESC"
            
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute(query, params) as cursor:
                    rows = await cursor.fetchall()
                    return [dict(row) for row in rows]
        
        except Exception as e:
            logger.error(f"Error getting trades: {e}")
            return []
    
    async def get_daily_performance(self, date: datetime) -> Dict:
        """Get daily performance metrics"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                
                # Get trades for the day
                start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
                end_date = start_date + timedelta(days=1)
                
                async with db.execute('''
                    SELECT * FROM trades 
                    WHERE timestamp >= ? AND timestamp < ? AND status = 'closed'
                ''', (start_date.isoformat(), end_date.isoformat())) as cursor:
                    trades = await cursor.fetchall()
                
                if not trades:
                    return {}
                
                # Calculate metrics
                total_trades = len(trades)
                winning_trades = sum(1 for trade in trades if trade['pnl'] > 0)
                losing_trades = total_trades - winning_trades
                
                gross_profit = sum(trade['pnl'] for trade in trades if trade['pnl'] > 0)
                gross_loss = sum(trade['pnl'] for trade in trades if trade['pnl'] < 0)
                net_profit = gross_profit + gross_loss
                
                win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
                profit_factor = abs(gross_profit / gross_loss) if gross_loss != 0 else 0
                
                avg_win = gross_profit / winning_trades if winning_trades > 0 else 0
                avg_loss = gross_loss / losing_trades if losing_trades > 0 else 0
                
                largest_win = max((trade['pnl'] for trade in trades if trade['pnl'] > 0), default=0)
                largest_loss = min((trade['pnl'] for trade in trades if trade['pnl'] < 0), default=0)
                
                return {
                    'date': date.date(),
                    'total_trades': total_trades,
                    'winning_trades': winning_trades,
                    'losing_trades': losing_trades,
                    'gross_profit': gross_profit,
                    'gross_loss': gross_loss,
                    'net_profit': net_profit,
                    'win_rate': win_rate,
                    'profit_factor': profit_factor,
                    'avg_win': avg_win,
                    'avg_loss': avg_loss,
                    'largest_win': largest_win,
                    'largest_loss': largest_loss
                }
        
        except Exception as e:
            logger.error(f"Error getting daily performance: {e}")
            return {}
    
    async def save_daily_performance(self, performance_data: Dict):
        """Save daily performance metrics"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    INSERT OR REPLACE INTO performance_metrics (
                        date, total_trades, winning_trades, losing_trades,
                        gross_profit, gross_loss, net_profit, profit_factor,
                        win_rate, avg_win, avg_loss, largest_win, largest_loss
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    performance_data['date'],
                    performance_data['total_trades'],
                    performance_data['winning_trades'],
                    performance_data['losing_trades'],
                    performance_data['gross_profit'],
                    performance_data['gross_loss'],
                    performance_data['net_profit'],
                    performance_data['profit_factor'],
                    performance_data['win_rate'],
                    performance_data['avg_win'],
                    performance_data['avg_loss'],
                    performance_data['largest_win'],
                    performance_data['largest_loss']
                ))
                await db.commit()
        
        except Exception as e:
            logger.error(f"Error saving daily performance: {e}")
    
    async def get_total_pnl(self) -> float:
        """Get total P&L from all closed trades"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute('''
                    SELECT COALESCE(SUM(pnl), 0) as total_pnl 
                    FROM trades WHERE status = 'closed'
                ''') as cursor:
                    result = await cursor.fetchone()
                    return result[0] if result else 0.0
        
        except Exception as e:
            logger.error(f"Error getting total P&L: {e}")
            return 0.0
    
    async def get_pair_performance(self, symbol: str, days: int = 30) -> Dict:
        """Get performance metrics for a specific trading pair"""
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                
                async with db.execute('''
                    SELECT * FROM trades 
                    WHERE symbol = ? AND timestamp >= ? AND status = 'closed'
                    ORDER BY timestamp DESC
                ''', (symbol, start_date.isoformat())) as cursor:
                    trades = await cursor.fetchall()
                
                if not trades:
                    return {}
                
                total_trades = len(trades)
                winning_trades = sum(1 for trade in trades if trade['pnl'] > 0)
                total_pnl = sum(trade['pnl'] for trade in trades)
                win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
                
                return {
                    'symbol': symbol,
                    'total_trades': total_trades,
                    'winning_trades': winning_trades,
                    'total_pnl': total_pnl,
                    'win_rate': win_rate,
                    'period_days': days
                }
        
        except Exception as e:
            logger.error(f"Error getting pair performance: {e}")
            return {}
    
    async def cache_market_data(self, symbol: str, timeframe: str, ohlcv_data: List):
        """Cache market data"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                for candle in ohlcv_data:
                    timestamp = datetime.fromtimestamp(candle[0] / 1000)
                    await db.execute('''
                        INSERT OR REPLACE INTO market_data 
                        (symbol, timestamp, timeframe, open_price, high_price, low_price, close_price, volume)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        symbol, timestamp, timeframe,
                        candle[1], candle[2], candle[3], candle[4], candle[5]
                    ))
                await db.commit()
        
        except Exception as e:
            logger.error(f"Error caching market data: {e}")
    
    async def get_cached_market_data(self, symbol: str, timeframe: str, 
                                   start_time: datetime, end_time: datetime) -> List:
        """Get cached market data"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute('''
                    SELECT timestamp, open_price, high_price, low_price, close_price, volume
                    FROM market_data 
                    WHERE symbol = ? AND timeframe = ? 
                    AND timestamp >= ? AND timestamp <= ?
                    ORDER BY timestamp
                ''', (symbol, timeframe, start_time.isoformat(), end_time.isoformat())) as cursor:
                    rows = await cursor.fetchall()
                    return [[
                        int(datetime.fromisoformat(row[0]).timestamp() * 1000),
                        row[1], row[2], row[3], row[4], row[5]
                    ] for row in rows]
        
        except Exception as e:
            logger.error(f"Error getting cached market data: {e}")
            return []
    
    async def log_ai_learning(self, pattern_name: str, success: bool, 
                            confidence: float, market_conditions: Dict, parameters: Dict):
        """Log AI learning data"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    INSERT INTO ai_learning 
                    (pattern_name, success, confidence, market_conditions, parameters)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    pattern_name, success, confidence,
                    json.dumps(market_conditions), json.dumps(parameters)
                ))
                await db.commit()
        
        except Exception as e:
            logger.error(f"Error logging AI learning data: {e}")
    
    async def get_ai_learning_data(self, pattern_name: Optional[str] = None, 
                                 days: int = 30) -> List[Dict]:
        """Get AI learning data"""
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            query = "SELECT * FROM ai_learning WHERE timestamp >= ?"
            params = [start_date.isoformat()]
            
            if pattern_name:
                query += " AND pattern_name = ?"
                params.append(pattern_name)
            
            query += " ORDER BY timestamp DESC"
            
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute(query, params) as cursor:
                    rows = await cursor.fetchall()
                    return [dict(row) for row in rows]
        
        except Exception as e:
            logger.error(f"Error getting AI learning data: {e}")
            return []
    
    async def backup_database(self, backup_path: Optional[str] = None):
        """Create database backup"""
        try:
            if backup_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = f"{self.db_path}.backup_{timestamp}"
            
            # Simple file copy for SQLite
            import shutil
            shutil.copy2(self.db_path, backup_path)
            
            logger.info(f"Database backed up to: {backup_path}")
            return backup_path
        
        except Exception as e:
            logger.error(f"Error backing up database: {e}")
            return None
    
    async def cleanup_old_data(self, days_to_keep: int = 90):
        """Clean up old data to manage database size"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            async with aiosqlite.connect(self.db_path) as db:
                # Clean old market data
                await db.execute('''
                    DELETE FROM market_data WHERE timestamp < ?
                ''', (cutoff_date.isoformat(),))
                
                # Clean old system logs
                await db.execute('''
                    DELETE FROM system_logs WHERE timestamp < ?
                ''', (cutoff_date.isoformat(),))
                
                # Clean old AI learning data (keep more recent)
                ai_cutoff = datetime.now() - timedelta(days=days_to_keep // 2)
                await db.execute('''
                    DELETE FROM ai_learning WHERE timestamp < ?
                ''', (ai_cutoff.isoformat(),))
                
                await db.commit()
            
            logger.info(f"Cleaned up data older than {days_to_keep} days")
        
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
