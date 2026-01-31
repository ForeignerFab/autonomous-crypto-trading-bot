"""
Pattern Research Module
Builds statistical evidence for trading patterns across markets.
"""

import time
import os
import json
from typing import Dict, List, Tuple
from datetime import datetime
import pandas as pd
import numpy as np
from loguru import logger


class PatternResearcher:
    """Run periodic research on trading patterns"""

    def __init__(self, config: Dict, okx_client, indicators, ai_assistant, db, discord):
        self.config = config
        self.okx_client = okx_client
        self.indicators = indicators
        self.ai_assistant = ai_assistant
        self.db = db
        self.discord = discord
        self._skip_symbols_path = os.path.join("data", "research_skip_symbols.json")
        self._skip_symbols = set()
        self._load_skip_symbols()

    async def run(self):
        settings = self.config.get('research', {})
        if not settings.get('enabled', False):
            return

        timeframes = settings.get('timeframes', ['1m', '5m', '15m'])
        days = int(settings.get('days', 90))
        top_pairs = int(settings.get('top_pairs', 30))
        max_requests = int(settings.get('max_requests_per_run', 2000))
        max_candles = int(settings.get('max_candles_per_timeframe', 20000))
        min_occurrences = int(settings.get('min_occurrences', 20))
        threshold = float(settings.get('min_return_threshold', 0.002))
        lookahead = settings.get('lookahead_candles', {"1m": 10, "5m": 6, "15m": 4})

        request_count = 0
        results = []

        allowlist = self.config.get('trading', {}).get('allowlist_pairs', [])
        if allowlist:
            tradeable = await self.okx_client.get_trading_pairs()
            allowset = {str(symbol).strip() for symbol in allowlist}
            symbols = [symbol for symbol in tradeable if symbol in allowset]
            if not symbols:
                await self.discord.send_notification(
                    "📚 Research Skipped",
                    "Allowlist filtered out all symbols for research."
                )
                return
        else:
            symbols = await self.okx_client.get_top_usdt_pairs(top_pairs)
        if not symbols:
            await self.discord.send_notification("📚 Research Skipped", "No symbols available for research.")
            return

        for symbol in symbols:
            if symbol in self._skip_symbols:
                continue
            for timeframe in timeframes:
                remaining_requests = max_requests - request_count
                if remaining_requests <= 0:
                    break

                df, used_requests = await self._fetch_history(
                    symbol, timeframe, days, max_candles, remaining_requests
                )
                request_count += used_requests

                if df is None or len(df) < 50:
                    continue

                indicators = await self.indicators.calculate_all(df)
                pattern_series = self._extract_patterns(indicators)
                timeframe_lookahead = int(lookahead.get(timeframe, 10))

                summary = self._analyze_patterns(
                    df, pattern_series, timeframe, threshold, timeframe_lookahead, min_occurrences
                )
                for record in summary:
                    record["symbol"] = symbol
                    record["timeframe"] = timeframe
                results.extend(summary)

            if request_count >= max_requests:
                break

        if results:
            await self.db.save_pattern_research(results)
            if self.ai_assistant:
                self.ai_assistant.apply_research_summary(results)
            await self.discord.send_research_summary(results, request_count, max_requests)
        else:
            await self.discord.send_notification("📚 Research Completed", "No pattern results found this run.")

    async def _fetch_history(
        self, symbol: str, timeframe: str, days: int, max_candles: int, max_requests: int
    ) -> Tuple[pd.DataFrame, int]:
        """Fetch historical OHLCV data with pagination"""
        now_ms = int(time.time() * 1000)
        since_ms = now_ms - int(days * 86400 * 1000)
        limit = 100

        target_candles = min(self._estimate_candles(days, timeframe), max_candles)
        all_candles = []
        used_requests = 0

        while len(all_candles) < target_candles and used_requests < max_requests:
            batch = await self.okx_client.get_klines_since(symbol, timeframe, since_ms, limit)
            used_requests += 1
            if not batch:
                if used_requests == 1:
                    self._skip_symbols.add(symbol)
                    self._save_skip_symbols()
                    logger.warning(
                        f"Skipping research for {symbol}; history-candles unavailable."
                    )
                break
            all_candles.extend(batch)
            since_ms = batch[-1][0] + 1

            if len(batch) < limit:
                break

        if not all_candles:
            return None, used_requests

        # Keep most recent candles up to target
        all_candles = all_candles[-target_candles:]
        df = pd.DataFrame(all_candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df = df.astype(float)
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

        return df, used_requests

    def _load_skip_symbols(self):
        try:
            if not os.path.exists(self._skip_symbols_path):
                return
            with open(self._skip_symbols_path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
            if isinstance(data, list):
                self._skip_symbols = set(str(item) for item in data)
                if self._skip_symbols:
                    logger.info(f"Loaded research skip list: {sorted(self._skip_symbols)}")
        except Exception as e:
            logger.warning(f"Failed to load research skip list: {e}")

    def _save_skip_symbols(self):
        try:
            os.makedirs(os.path.dirname(self._skip_symbols_path), exist_ok=True)
            with open(self._skip_symbols_path, "w", encoding="utf-8") as handle:
                json.dump(sorted(self._skip_symbols), handle, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save research skip list: {e}")

    def _extract_patterns(self, indicators: Dict) -> Dict[str, pd.Series]:
        """Extract known pattern series from indicators"""
        keys = [
            'doji',
            'hammer',
            'engulfing',
            'higher_highs',
            'lower_lows',
            'double_top',
            'double_bottom'
        ]
        patterns = {}
        for key in keys:
            series = indicators.get(key)
            if isinstance(series, pd.Series):
                patterns[key] = series
        return patterns

    def _analyze_patterns(
        self,
        df: pd.DataFrame,
        patterns: Dict[str, pd.Series],
        timeframe: str,
        threshold: float,
        lookahead: int,
        min_occurrences: int
    ) -> List[Dict]:
        """Evaluate pattern success rates"""
        close = df['close'].values
        results = []

        direction_map = {
            'hammer': 'bullish',
            'engulfing': 'bullish',
            'doji': 'neutral',
            'higher_highs': 'bullish',
            'lower_lows': 'bearish',
            'double_top': 'bearish',
            'double_bottom': 'bullish'
        }

        for pattern_name, series in patterns.items():
            positions = np.where(series.values > 0)[0]
            if len(positions) < min_occurrences:
                continue

            returns = []
            successes = 0
            direction = direction_map.get(pattern_name, 'neutral')

            for pos in positions:
                if pos + lookahead >= len(close):
                    continue
                ret = (close[pos + lookahead] - close[pos]) / close[pos]
                returns.append(ret)

                if direction == 'bullish' and ret >= threshold:
                    successes += 1
                elif direction == 'bearish' and ret <= -threshold:
                    successes += 1
                elif direction == 'neutral' and abs(ret) >= threshold:
                    successes += 1

            if not returns:
                continue

            results.append({
                "pattern_name": pattern_name,
                "occurrences": int(len(positions)),
                "success_rate": float(successes / len(returns)),
                "avg_return": float(np.mean(returns)),
                "sample_size": int(len(returns)),
                "timeframe": timeframe
            })

        return results

    def _estimate_candles(self, days: int, timeframe: str) -> int:
        minutes_map = {"1m": 1, "5m": 5, "15m": 15}
        minutes = minutes_map.get(timeframe, 1)
        return int(days * 24 * 60 / minutes)
