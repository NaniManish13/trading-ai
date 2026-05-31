"""
Market data service using yfinance with caching and batch downloading.
"""
import logging
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class MarketDataService:
    """Fetch and manage market data with caching."""

    HISTORY_TTL_SECONDS = 900  # 15 minutes
    BATCH_SIZE = 50
    DEFAULT_TIMEOUT = 15
    MAX_RETRIES = 3

    _history_cache: Dict[Tuple[str, str, str], Tuple[datetime, pd.DataFrame]] = {}

    @staticmethod
    def _cache_get(cache: Dict, key: Tuple, ttl: int):
        cached = cache.get(key)
        if not cached:
            return None
        timestamp, value = cached
        if datetime.utcnow() - timestamp > timedelta(seconds=ttl):
            cache.pop(key, None)
            return None
        return value

    @staticmethod
    def _cache_set(cache: Dict, key: Tuple, value, ttl: int):
        cache[key] = (datetime.utcnow(), value)

    @staticmethod
    def get_ohlcv(symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
        """Fetch OHLCV data for a single symbol with caching."""
        symbol = symbol.strip().upper()
        cache_key = (symbol, period, interval)
        cached = MarketDataService._cache_get(MarketDataService._history_cache, cache_key, MarketDataService.HISTORY_TTL_SECONDS)
        if cached is not None:
            return cached.copy()

        for attempt in range(1, MarketDataService.MAX_RETRIES + 1):
            try:
                data = yf.download(
                    symbol,
                    period=period,
                    interval=interval,
                    progress=False,
                    timeout=MarketDataService.DEFAULT_TIMEOUT,
                    threads=False,
                )
                if data.empty:
                    raise ValueError(f"No OHLCV data for {symbol}")
                data = data.rename(columns={
                    'Open': 'open',
                    'High': 'high',
                    'Low': 'low',
                    'Close': 'close',
                    'Volume': 'volume'
                })
                MarketDataService._cache_set(MarketDataService._history_cache, cache_key, data, MarketDataService.HISTORY_TTL_SECONDS)
                return data
            except Exception as exc:
                logger.warning(f"Attempt {attempt}/{MarketDataService.MAX_RETRIES} failed for {symbol}: {exc}")
                if attempt == MarketDataService.MAX_RETRIES:
                    logger.error(f"get_ohlcv failed for {symbol}: {exc}")
                    return pd.DataFrame()

        return pd.DataFrame()

    @staticmethod
    def get_ohlcv_batch(symbols: List[str], period: str = "6mo", interval: str = "1d") -> Dict[str, pd.DataFrame]:
        """Fetch OHLCV data for a list of symbols using batch downloads."""
        results: Dict[str, pd.DataFrame] = {}
        symbols = [sym.strip().upper() for sym in symbols if sym]
        
        for batch_start in range(0, len(symbols), MarketDataService.BATCH_SIZE):
            batch = symbols[batch_start:batch_start + MarketDataService.BATCH_SIZE]
            try:
                logger.info(f"Batch downloading {len(batch)} symbols")
                data = yf.download(
                    tickers=batch,
                    period=period,
                    interval=interval,
                    group_by='ticker',
                    progress=False,
                    timeout=MarketDataService.DEFAULT_TIMEOUT,
                    threads=True,
                )
                if data.empty:
                    raise ValueError("Batch download returned empty data")

                for symbol in batch:
                    cache_key = (symbol, period, interval)
                    if isinstance(data.columns, pd.MultiIndex):
                        try:
                            df = data[symbol].copy()
                        except KeyError:
                            df = pd.DataFrame()
                    else:
                        df = data.copy()
                    if not df.empty:
                        df = df.rename(columns={
                            'Open': 'open',
                            'High': 'high',
                            'Low': 'low',
                            'Close': 'close',
                            'Volume': 'volume'
                        })
                        MarketDataService._cache_set(MarketDataService._history_cache, cache_key, df, MarketDataService.HISTORY_TTL_SECONDS)
                        results[symbol] = df
                    else:
                        results[symbol] = pd.DataFrame()
            except Exception as exc:
                logger.warning(f"Batch download failed for {batch}: {exc}")
                for symbol in batch:
                    results[symbol] = MarketDataService.get_ohlcv(symbol, period=period, interval=interval)

        return results

    @staticmethod
    def get_current_price(symbol: str) -> Optional[float]:
        """Get current price for a symbol."""
        symbol = symbol.strip().upper()
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.fast_info if hasattr(ticker, 'fast_info') else ticker.info
            price = info.get('last_price') or info.get('currentPrice') or info.get('regularMarketPrice')
            return float(price) if price else None
        except Exception as e:
            logger.error(f"Error getting current price for {symbol}: {e}")
            return None

    @staticmethod
    def get_intraday_data(symbol: str, interval: str = "5m") -> pd.DataFrame:
        """Get intraday data."""
        try:
            data = yf.download(symbol, period="1d", interval=interval, progress=False, timeout=MarketDataService.DEFAULT_TIMEOUT)
            if data.empty:
                logger.warning(f"No intraday data for {symbol}")
                return pd.DataFrame()
            return data
        except Exception as e:
            logger.error(f"Error fetching intraday data: {e}")
            return pd.DataFrame()

    @staticmethod
    def get_volume_profile(symbol: str, days: int = 20) -> Dict:
        """Analyze volume profile for a symbol."""
        try:
            data = MarketDataService.get_ohlcv(symbol, period=f"{days}d")
            if data.empty or 'volume' not in data.columns:
                return {}
            avg_volume = data['volume'].mean()
            current_volume = data['volume'].iloc[-1]
            volume_ratio = float(current_volume / avg_volume) if avg_volume and avg_volume > 0 else 0
            return {
                'avg_volume': float(avg_volume),
                'current_volume': float(current_volume),
                'volume_ratio': volume_ratio,
                'is_breakout': volume_ratio > 1.5
            }
        except Exception as e:
            logger.error(f"Error analyzing volume for {symbol}: {e}")
            return {}

    @staticmethod
    def get_52week_high_low(symbol: str) -> Dict:
        """Get 52-week high and low values."""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            return {
                'high_52week': info.get('fiftyTwoWeekHigh', 0),
                'low_52week': info.get('fiftyTwoWeekLow', 0),
                'current_price': info.get('regularMarketPrice', 0)
            }
        except Exception as e:
            logger.error(f"Error getting 52-week data: {e}")
            return {}
