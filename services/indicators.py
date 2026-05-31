"""
Technical indicators service
"""
import logging
import pandas as pd
import numpy as np
from typing import Dict
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator, MACD
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
            return {
                'macd': pd.Series(dtype=float),
                'macd_signal': pd.Series(dtype=float),
                'macd_diff': pd.Series(dtype=float)
            }

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
    def get_all_indicators(data: pd.DataFrame) -> pd.DataFrame:
        """Calculate all indicators"""
        try:
            data = data.copy()
            data.columns = [c.lower() for c in data.columns]

            data['rsi'] = IndicatorsService.calculate_rsi(data)
            data['ema_fast'] = IndicatorsService.calculate_ema(data, EMA_FAST)
            data['ema_slow'] = IndicatorsService.calculate_ema(data, EMA_SLOW)

            macd_dict = IndicatorsService.calculate_macd(data)
            data['macd'] = macd_dict.get('macd', pd.Series(dtype=float))
            data['macd_signal'] = macd_dict.get('macd_signal', pd.Series(dtype=float))
            data['macd_diff'] = macd_dict.get('macd_diff', pd.Series(dtype=float))

            data['atr'] = IndicatorsService.calculate_atr(data)
            data['ema_trend'] = np.where(data['ema_fast'] > data['ema_slow'], 'BULLISH', 'BEARISH')
            data['volume_avg'] = data['volume'].rolling(window=20, min_periods=10).mean()
            data['volume_spike'] = np.where(data['volume'] > data['volume_avg'] * 1.5, True, False)

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
                    'rsi': 0,
                    'ema_fast': 0,
                    'ema_slow': 0,
                    'macd': 0,
                    'macd_signal': 0,
                    'atr': 0,
                    'volume_spike': False,
                    'bullish_score': 0,
                    'bearish_score': 0,
                    'final_score': 0,
                    'ema_status': 'UNKNOWN',
                    'macd_status': 'UNKNOWN',
                    'details': 'Not enough data for analysis'
                }

            data_with_indicators = IndicatorsService.get_all_indicators(data)
            latest = data_with_indicators.iloc[-1]

            rsi = float(latest.get('rsi', 50))
            ema_fast = float(latest.get('ema_fast', 0))
            ema_slow = float(latest.get('ema_slow', 0))
            macd = float(latest.get('macd', 0))
            macd_signal = float(latest.get('macd_signal', 0))
            atr = float(latest.get('atr', 0))
            volume_spike = bool(latest.get('volume_spike', False))
            current_volume = float(latest.get('volume', 0)) if 'volume' in latest else 0
            avg_volume = float(latest.get('volume_avg', 0)) if 'volume_avg' in latest else 0
            volume_ratio = float(current_volume / avg_volume) if avg_volume > 0 else 0

            bullish_score = 0.0
            bearish_score = 0.0
            signals = []

            if rsi < RSI_OVERSOLD:
                bullish_score += 1.5
                signals.append('RSI_OVERSOLD')
            elif rsi > RSI_OVERBOUGHT:
                bearish_score += 1.5
                signals.append('RSI_OVERBOUGHT')
            else:
                signals.append('RSI_NEUTRAL')

            if ema_fast > ema_slow:
                bullish_score += 1.2
                ema_status = 'BULLISH'
            else:
                bearish_score += 1.2
                ema_status = 'BEARISH'

            if macd > macd_signal:
                bullish_score += 1.2
                macd_status = 'BULLISH'
            else:
                bearish_score += 1.2
                macd_status = 'BEARISH'

            if volume_spike:
                bullish_score += 0.8
                signals.append('VOLUME_SPIKE')

            if current_volume and avg_volume:
                volume_score = min(volume_ratio, 3.0)
            else:
                volume_score = 0.0

            if latest.get('close', 0) > latest.get('open', 0):
                bullish_score += 0.5
            else:
                bearish_score += 0.2

            final_score = round(bullish_score - bearish_score, 3)
            technical_signal = 'BUY' if final_score > 0.5 else ('SELL' if final_score < -0.5 else 'HOLD')
            confidence = min(max(abs(final_score) / 5, 0), 1)

            return {
                'technical_signal': technical_signal,
                'confidence': confidence,
                'rsi': rsi,
                'ema_fast': ema_fast,
                'ema_slow': ema_slow,
                'macd': macd,
                'macd_signal': macd_signal,
                'atr': atr,
                'volume_spike': volume_spike,
                'volume_ratio': round(volume_ratio, 2),
                'bullish_score': bullish_score,
                'bearish_score': bearish_score,
                'final_score': final_score,
                'ema_status': ema_status,
                'macd_status': macd_status,
                'details': {
                    'signals': signals,
                    'volume_score': volume_score
                }
            }
        except Exception as e:
            logger.error(f"Error analyzing signals: {e}")
            return {
                'technical_signal': 'ERROR',
                'confidence': 0,
                'rsi': 0,
                'ema_fast': 0,
                'ema_slow': 0,
                'macd': 0,
                'macd_signal': 0,
                'atr': 0,
                'volume_spike': False,
                'bullish_score': 0,
                'bearish_score': 0,
                'final_score': 0,
                'ema_status': 'UNKNOWN',
                'macd_status': 'UNKNOWN',
                'details': str(e)
            }
