"""
Technical indicators service
"""
import logging
import pandas as pd
import numpy as np
from typing import Dict, Optional
from ta.momentum import RSIIndicator, MACD
from ta.trend import EMAIndicator
from ta.volatility import AverageTrueRange
from config.settings import (
    EMA_FAST, EMA_SLOW, RSI_PERIOD, MACD_FAST, 
    MACD_SLOW, MACD_SIGNAL, ATR_PERIOD,
    RSI_OVERBOUGHT, RSI_OVERSOLD
)

logger = logging.getLogger(__name__)


class IndicatorsService:
    """Calculate technical indicators"""
    
    @staticmethod
    def calculate_rsi(data: pd.DataFrame, period: int = RSI_PERIOD) -> pd.Series:
        """Calculate Relative Strength Index"""
        try:
            rsi = RSIIndicator(close=data['close'], window=period)
            return rsi.rsi()
        except Exception as e:
            logger.error(f"Error calculating RSI: {e}")
            return pd.Series(dtype=float)
    
    @staticmethod
    def calculate_ema(data: pd.DataFrame, period: int) -> pd.Series:
        """Calculate Exponential Moving Average"""
        try:
            ema = EMAIndicator(close=data['close'], window=period)
            return ema.ema_indicator()
        except Exception as e:
            logger.error(f"Error calculating EMA: {e}")
            return pd.Series(dtype=float)
    
    @staticmethod
    def calculate_macd(data: pd.DataFrame) -> Dict[str, pd.Series]:
        """Calculate MACD"""
        try:
            macd = MACD(
                close=data['close'],
                window_fast=MACD_FAST,
                window_slow=MACD_SLOW,
                window_sign=MACD_SIGNAL
            )
            return {
                'macd': macd.macd(),
                'macd_signal': macd.macd_signal(),
                'macd_diff': macd.macd_diff()
            }
        except Exception as e:
            logger.error(f"Error calculating MACD: {e}")
            return {}
    
    @staticmethod
    def calculate_atr(data: pd.DataFrame, period: int = ATR_PERIOD) -> pd.Series:
        """Calculate Average True Range"""
        try:
            atr = AverageTrueRange(
                high=data['high'],
                low=data['low'],
                close=data['close'],
                window=period
            )
            return atr.average_true_range()
        except Exception as e:
            logger.error(f"Error calculating ATR: {e}")
            return pd.Series(dtype=float)
    
    @staticmethod
    def get_all_indicators(data: pd.DataFrame) -> Dict:
        """Calculate all indicators"""
        try:
            data = data.copy()
            data.columns = [c.lower() for c in data.columns]
            
            # Calculate indicators
            data['rsi'] = IndicatorsService.calculate_rsi(data)
            data['ema_fast'] = IndicatorsService.calculate_ema(data, EMA_FAST)
            data['ema_slow'] = IndicatorsService.calculate_ema(data, EMA_SLOW)
            
            macd_dict = IndicatorsService.calculate_macd(data)
            data['macd'] = macd_dict.get('macd', pd.Series(dtype=float))
            data['macd_signal'] = macd_dict.get('macd_signal', pd.Series(dtype=float))
            data['macd_diff'] = macd_dict.get('macd_diff', pd.Series(dtype=float))
            
            data['atr'] = IndicatorsService.calculate_atr(data)
            
            return data
        except Exception as e:
            logger.error(f"Error calculating all indicators: {e}")
            return pd.DataFrame()
    
    @staticmethod
    def get_signal_analysis(data: pd.DataFrame) -> Dict:
        """Analyze signals from indicators"""
        try:
            if data.empty or len(data) < 50:
                return {
                    'technical_signal': 'INSUFFICIENT_DATA',
                    'confidence': 0,
                    'details': 'Not enough data for analysis'
                }
            
            data_with_indicators = IndicatorsService.get_all_indicators(data)
            latest = data_with_indicators.iloc[-1]
            
            signals = []
            
            # RSI Signal
            rsi = latest.get('rsi', 50)
            if rsi < RSI_OVERSOLD:
                signals.append(('RSI_OVERSOLD', 0.8))
            elif rsi > RSI_OVERBOUGHT:
                signals.append(('RSI_OVERBOUGHT', 0.8))
            else:
                signals.append(('RSI_NEUTRAL', 0.3))
            
            # EMA Crossover Signal
            ema_fast = latest.get('ema_fast', 0)
            ema_slow = latest.get('ema_slow', 0)
            if ema_fast > ema_slow:
                signals.append(('EMA_BULLISH', 0.7))
            else:
                signals.append(('EMA_BEARISH', 0.7))
            
            # MACD Signal
            macd = latest.get('macd', 0)
            macd_signal = latest.get('macd_signal', 0)
            macd_diff = latest.get('macd_diff', 0)
            if macd > macd_signal:
                signals.append(('MACD_BULLISH', 0.6))
            else:
                signals.append(('MACD_BEARISH', 0.6))
            
            # Calculate overall signal
            bullish_count = sum(1 for s in signals if 'BULLISH' in s[0] or 'OVERSOLD' in s[0])
            bearish_count = sum(1 for s in signals if 'BEARISH' in s[0] or 'OVERBOUGHT' in s[0])
            
            if bullish_count > bearish_count:
                technical_signal = 'BUY'
            elif bearish_count > bullish_count:
                technical_signal = 'SELL'
            else:
                technical_signal = 'HOLD'
            
            avg_confidence = sum(s[1] for s in signals) / len(signals)
            
            return {
                'technical_signal': technical_signal,
                'confidence': avg_confidence,
                'rsi': float(rsi),
                'ema_fast': float(ema_fast),
                'ema_slow': float(ema_slow),
                'macd': float(macd),
                'macd_signal': float(macd_signal),
                'atr': float(latest.get('atr', 0)),
                'details': str(signals)
            }
        except Exception as e:
            logger.error(f"Error analyzing signals: {e}")
            return {'technical_signal': 'ERROR', 'confidence': 0, 'details': str(e)}
