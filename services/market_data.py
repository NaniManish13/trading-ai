"""
Market data service using yfinance
"""
import logging
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class MarketDataService:
    """Fetch and manage market data"""
    
    @staticmethod
    def get_ohlcv(
        symbol: str, 
        period: str = "1y", 
        interval: str = "1d"
    ) -> pd.DataFrame:
        """
        Fetch OHLCV data for a symbol
        
        Args:
            symbol: Stock ticker
            period: Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1m, 5m, 15m, 30m, 60m, 1d, 1wk, 1mo)
        
        Returns:
            DataFrame with OHLCV data
        """
        try:
            data = yf.download(symbol, period=period, interval=interval, progress=False)
            if data.empty:
                logger.warning(f"No data found for {symbol}")
                return pd.DataFrame()
            
            data = data.rename(columns={
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume'
            })
            
            return data
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            return pd.DataFrame()
    
    @staticmethod
    def get_current_price(symbol: str) -> Optional[float]:
        """Get current price for a symbol"""
        try:
            ticker = yf.Ticker(symbol)
            price = ticker.info.get('currentPrice') or ticker.info.get('regularMarketPrice')
            return price
        except Exception as e:
            logger.error(f"Error getting current price for {symbol}: {e}")
            return None
    
    @staticmethod
    def get_intraday_data(symbol: str, interval: str = "5m") -> pd.DataFrame:
        """Get intraday data"""
        try:
            data = yf.download(symbol, period="1d", interval=interval, progress=False)
            if data.empty:
                logger.warning(f"No intraday data for {symbol}")
                return pd.DataFrame()
            return data
        except Exception as e:
            logger.error(f"Error fetching intraday data: {e}")
            return pd.DataFrame()
    
    @staticmethod
    def get_multiple_ohlcv(
        symbols: List[str], 
        period: str = "1y"
    ) -> Dict[str, pd.DataFrame]:
        """Fetch OHLCV for multiple symbols"""
        results = {}
        for symbol in symbols:
            results[symbol] = MarketDataService.get_ohlcv(symbol, period)
        return results
    
    @staticmethod
    def get_volume_profile(symbol: str, days: int = 20) -> Dict:
        """Analyze volume profile"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            data = yf.download(
                symbol, 
                start=start_date, 
                end=end_date, 
                progress=False
            )
            
            if data.empty:
                return {}
            
            avg_volume = data['Volume'].mean()
            max_volume = data['Volume'].max()
            current_volume = data['Volume'].iloc[-1]
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 0
            
            return {
                'avg_volume': avg_volume,
                'max_volume': max_volume,
                'current_volume': current_volume,
                'volume_ratio': volume_ratio,
                'is_breakout': volume_ratio > 1.5
            }
        except Exception as e:
            logger.error(f"Error analyzing volume: {e}")
            return {}
    
    @staticmethod
    def get_52week_high_low(symbol: str) -> Dict:
        """Get 52-week high and low"""
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
