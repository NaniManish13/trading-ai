"""
Technical Analysis Agent - Evaluates technical indicators
"""
import logging
import pandas as pd
from typing import Dict, Tuple
from services.market_data import MarketDataService
from services.indicators import IndicatorsService
from config.settings import RSI_OVERBOUGHT, RSI_OVERSOLD

logger = logging.getLogger(__name__)


class TechnicalAgent:
    """Technical analysis agent using indicators"""
    
    def __init__(self):
        """Initialize technical agent"""
        self.market_data_service = MarketDataService()
        self.indicators_service = IndicatorsService()
    
    def analyze(self, symbol: str, period: str = "6mo") -> Dict:
        """
        Comprehensive technical analysis for a symbol
        
        Args:
            symbol: Stock ticker
            period: Data period for analysis
        
        Returns:
            Dict with technical analysis results
        """
        try:
            # Get data
            data = self.market_data_service.get_ohlcv(symbol, period=period)
            if data.empty or len(data) < 50:
                return {
                    'symbol': symbol,
                    'signal': 'INSUFFICIENT_DATA',
                    'confidence': 0,
                    'score': 0,
                    'details': {}
                }
            
            # Get indicators
            signal_analysis = IndicatorsService.get_signal_analysis(data)
            
            # Calculate scores
            bullish_score, bearish_score = self._calculate_scores(data)
            
            # Determine signal
            if bullish_score > bearish_score:
                signal = 'BUY'
            elif bearish_score > bullish_score:
                signal = 'SELL'
            else:
                signal = 'HOLD'
            
            overall_score = (bullish_score - bearish_score) / (bullish_score + bearish_score) if (bullish_score + bearish_score) > 0 else 0
            
            return {
                'symbol': symbol,
                'signal': signal,
                'confidence': signal_analysis.get('confidence', 0),
                'score': overall_score,
                'bullish_score': bullish_score,
                'bearish_score': bearish_score,
                'details': signal_analysis,
            }
        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {e}")
            return {
                'symbol': symbol,
                'signal': 'ERROR',
                'confidence': 0,
                'score': 0,
                'details': str(e)
            }
    
    def _calculate_scores(self, data: pd.DataFrame) -> Tuple[float, float]:
        """Calculate bullish and bearish scores"""
        try:
            data = data.copy()
            data.columns = [c.lower() for c in data.columns]
            
            bullish_score = 0
            bearish_score = 0
            
            # RSI analysis
            rsi = IndicatorsService.calculate_rsi(data)
            if not rsi.empty:
                latest_rsi = rsi.iloc[-1]
                if latest_rsi < RSI_OVERSOLD:
                    bullish_score += 2
                elif latest_rsi > RSI_OVERBOUGHT:
                    bearish_score += 2
            
            # EMA analysis
            ema_fast = IndicatorsService.calculate_ema(data, 20)
            ema_slow = IndicatorsService.calculate_ema(data, 50)
            if not ema_fast.empty and not ema_slow.empty:
                if ema_fast.iloc[-1] > ema_slow.iloc[-1]:
                    bullish_score += 1.5
                else:
                    bearish_score += 1.5
            
            # MACD analysis
            macd_dict = IndicatorsService.calculate_macd(data)
            if macd_dict:
                macd = macd_dict.get('macd')
                macd_signal = macd_dict.get('macd_signal')
                if not macd.empty and not macd_signal.empty:
                    if macd.iloc[-1] > macd_signal.iloc[-1]:
                        bullish_score += 1.5
                    else:
                        bearish_score += 1.5
            
            # Price momentum
            if len(data) >= 20:
                current_close = data['close'].iloc[-1]
                sma_20 = data['close'].iloc[-20:].mean()
                if current_close > sma_20:
                    bullish_score += 1
                else:
                    bearish_score += 1
            
            return bullish_score, bearish_score
        except Exception as e:
            logger.error(f"Error calculating scores: {e}")
            return 0, 0
    
    def get_support_resistance(self, data: pd.DataFrame) -> Dict:
        """Identify support and resistance levels"""
        try:
            if data.empty:
                return {}
            
            # Get highs and lows
            highs = data['high'].tail(50)
            lows = data['low'].tail(50)
            
            resistance = highs.max()
            support = lows.min()
            current_price = data['close'].iloc[-1]
            
            return {
                'resistance': resistance,
                'support': support,
                'current_price': current_price,
                'distance_to_resistance': ((resistance - current_price) / current_price * 100) if current_price > 0 else 0,
                'distance_to_support': ((current_price - support) / current_price * 100) if current_price > 0 else 0,
            }
        except Exception as e:
            logger.error(f"Error getting support resistance: {e}")
            return {}
    
    def get_trend(self, data: pd.DataFrame) -> str:
        """Identify current trend"""
        try:
            if len(data) < 50:
                return 'INSUFFICIENT_DATA'
            
            # Compare close to 50-day MA
            sma_50 = data['close'].tail(50).mean()
            current_close = data['close'].iloc[-1]
            
            if current_close > sma_50 * 1.02:
                return 'UPTREND'
            elif current_close < sma_50 * 0.98:
                return 'DOWNTREND'
            else:
                return 'SIDEWAYS'
        except Exception as e:
            logger.error(f"Error identifying trend: {e}")
            return 'ERROR'
