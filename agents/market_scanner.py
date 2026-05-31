"""
Market Scanner Agent - Identifies trading opportunities
"""
import logging
import pandas as pd
from typing import Dict, List
from services.market_data import MarketDataService
from services.indicators import IndicatorsService
from config.settings import NIFTY_50_STOCKS

logger = logging.getLogger(__name__)


class MarketScannerAgent:
    """Scan market for trading opportunities"""
    
    def __init__(self):
        """Initialize market scanner"""
        self.market_data_service = MarketDataService()
        self.indicators_service = IndicatorsService()
    
    def scan_market(self, symbols: List[str] = None) -> Dict:
        """
        Scan multiple stocks for opportunities
        
        Args:
            symbols: List of stock symbols to scan
        
        Returns:
            Dict with scan results
        """
        if symbols is None:
            symbols = NIFTY_50_STOCKS[:20]  # Start with first 20 for performance
        
        opportunities = []
        errors = []
        
        for symbol in symbols:
            try:
                result = self.scan_symbol(symbol)
                if result:
                    opportunities.append(result)
            except Exception as e:
                logger.warning(f"Error scanning {symbol}: {e}")
                errors.append((symbol, str(e)))
        
        return {
            'timestamp': pd.Timestamp.now(),
            'total_scanned': len(symbols),
            'opportunities': opportunities,
            'errors': errors,
            'total_opportunities': len(opportunities),
        }
    
    def scan_symbol(self, symbol: str) -> Dict:
        """
        Scan a single symbol
        
        Args:
            symbol: Stock ticker
        
        Returns:
            Dict with symbol scan results
        """
        try:
            # Get price data
            data = self.market_data_service.get_ohlcv(symbol, period="6mo")
            if data.empty or len(data) < 50:
                return {}
            
            # Get technical analysis
            technical_analysis = IndicatorsService.get_signal_analysis(data)
            
            # Get volume profile
            volume_profile = self.market_data_service.get_volume_profile(symbol)
            
            # Get 52-week data
            week_52 = self.market_data_service.get_52week_high_low(symbol)
            
            latest = data.iloc[-1]
            
            return {
                'symbol': symbol,
                'current_price': float(latest.get('close', 0)),
                'technical_signal': technical_analysis.get('technical_signal', 'UNKNOWN'),
                'technical_confidence': technical_analysis.get('confidence', 0),
                'rsi': technical_analysis.get('rsi', 0),
                'ema_fast': technical_analysis.get('ema_fast', 0),
                'ema_slow': technical_analysis.get('ema_slow', 0),
                'volume_ratio': volume_profile.get('volume_ratio', 0),
                'is_volume_breakout': volume_profile.get('is_breakout', False),
                'week_52_high': week_52.get('high_52week', 0),
                'week_52_low': week_52.get('low_52week', 0),
                'distance_from_high_percent': ((week_52.get('high_52week', 1) - float(latest.get('close', 0))) / week_52.get('high_52week', 1) * 100) if week_52.get('high_52week') else 0,
                'distance_from_low_percent': ((float(latest.get('close', 0)) - week_52.get('low_52week', 0)) / week_52.get('low_52week', 1) * 100) if week_52.get('low_52week') else 0,
            }
        except Exception as e:
            logger.error(f"Error scanning symbol {symbol}: {e}")
            return {}
    
    def get_top_opportunities(self, opportunities: List[Dict], limit: int = 10) -> List[Dict]:
        """
        Get top trading opportunities based on technical signals
        
        Args:
            opportunities: List of scan results
            limit: Number of top opportunities to return
        
        Returns:
            Sorted list of top opportunities
        """
        try:
            # Score opportunities
            scored = []
            for opp in opportunities:
                if opp.get('technical_signal') == 'BUY':
                    base_score = opp.get('technical_confidence', 0)
                    volume_bonus = 0.1 if opp.get('is_volume_breakout') else 0
                    total_score = base_score + volume_bonus
                    
                    scored.append({
                        **opp,
                        'opportunity_score': total_score
                    })
            
            # Sort by opportunity score
            scored.sort(key=lambda x: x['opportunity_score'], reverse=True)
            return scored[:limit]
        except Exception as e:
            logger.error(f"Error getting top opportunities: {e}")
            return []
    
    def detect_ema_crossover(self, data: pd.DataFrame) -> str:
        """Detect EMA crossover signals"""
        try:
            if len(data) < 2:
                return 'INSUFFICIENT_DATA'
            
            # Calculate EMAs
            ema_fast = IndicatorsService.calculate_ema(data, 20)
            ema_slow = IndicatorsService.calculate_ema(data, 50)
            
            current_fast = ema_fast.iloc[-1]
            current_slow = ema_slow.iloc[-1]
            prev_fast = ema_fast.iloc[-2]
            prev_slow = ema_slow.iloc[-2]
            
            # Check crossover
            if prev_fast <= prev_slow and current_fast > current_slow:
                return 'BULLISH_CROSSOVER'
            elif prev_fast >= prev_slow and current_fast < current_slow:
                return 'BEARISH_CROSSOVER'
            else:
                return 'NO_CROSSOVER'
        except Exception as e:
            logger.error(f"Error detecting EMA crossover: {e}")
            return 'ERROR'
