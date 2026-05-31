"""
Market Scanner Agent - Identifies trading opportunities
"""
import logging
import traceback
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
        scan_log = []
        successful_fetches = 0
        failed_fetches = 0
        indicator_failures = 0
        buy_opportunity_count = 0

        for symbol in symbols:
            entry = {
                'symbol': symbol,
                'rows_fetched': 0,
                'current_price': None,
                'rsi': None,
                'ema20': None,
                'ema50': None,
                'macd': None,
                'technical_signal': 'UNKNOWN',
                'technical_confidence': 0,
                'status': 'UNKNOWN',
                'fetch_reason': None,
                'indicator_reason': None,
                'error': None,
            }

            try:
                result = self.scan_symbol(symbol)
                entry.update({
                    'rows_fetched': result.get('rows_fetched', 0),
                    'current_price': result.get('current_price'),
                    'rsi': result.get('rsi'),
                    'ema20': result.get('ema20'),
                    'ema50': result.get('ema50'),
                    'macd': result.get('macd'),
                    'technical_signal': result.get('technical_signal', 'UNKNOWN'),
                    'technical_confidence': result.get('technical_confidence', 0),
                    'status': result.get('status', 'UNKNOWN'),
                    'fetch_reason': result.get('fetch_reason'),
                    'indicator_reason': result.get('indicator_reason'),
                    'error': result.get('error'),
                })

                if result.get('status') == 'SCANNED':
                    successful_fetches += 1
                    opportunities.append(result)
                    if result.get('technical_signal') == 'BUY':
                        buy_opportunity_count += 1
                elif result.get('status') == 'INDICATOR_FAILED':
                    successful_fetches += 1
                    indicator_failures += 1
                else:
                    failed_fetches += 1
                    if result.get('status') == 'FETCH_FAILED':
                        errors.append({'symbol': symbol, 'error': result.get('fetch_reason') or result.get('error')})

            except Exception:
                failed_fetches += 1
                trace = traceback.format_exc()
                entry['status'] = 'ERROR'
                entry['error'] = trace
                errors.append({'symbol': symbol, 'error': trace})
                logger.exception("Unhandled exception scanning %s", symbol)

            scan_log.append(entry)
            logger.info(
                "Scanned symbol=%s rows=%s price=%s RSI=%s EMA20=%s EMA50=%s signal=%s status=%s",
                symbol,
                entry['rows_fetched'],
                entry['current_price'],
                entry['rsi'],
                entry['ema20'],
                entry['ema50'],
                entry['technical_signal'],
                entry['status'],
            )

        return {
            'timestamp': pd.Timestamp.now(),
            'total_scanned': len(symbols),
            'successful_fetches': successful_fetches,
            'failed_fetches': failed_fetches,
            'indicator_failures': indicator_failures,
            'opportunities': opportunities,
            'errors': errors,
            'scan_log': scan_log,
            'total_opportunities': buy_opportunity_count,
        }
    
    def scan_symbol(self, symbol: str) -> Dict:
        """
        Scan a single symbol
        
        Args:
            symbol: Stock ticker
        
        Returns:
            Dict with symbol scan results
        """
        result = {
            'symbol': symbol,
            'rows_fetched': 0,
            'current_price': None,
            'technical_signal': 'UNKNOWN',
            'technical_confidence': 0,
            'rsi': None,
            'ema20': None,
            'ema50': None,
            'macd': None,
            'volume_ratio': None,
            'is_volume_breakout': False,
            'week_52_high': 0,
            'week_52_low': 0,
            'distance_from_high_percent': 0,
            'distance_from_low_percent': 0,
            'status': 'UNKNOWN',
            'fetch_reason': None,
            'indicator_reason': None,
            'error': None,
        }

        try:
            data = self.market_data_service.get_ohlcv(symbol, period="6mo")
            if data is None or data.empty:
                reason = "get_ohlcv returned no data"
                logger.warning("%s | rows=%s | %s", symbol, 0, reason)
                result.update(status='FETCH_FAILED', fetch_reason=reason, error=reason)
                return result

            rows = len(data)
            result['rows_fetched'] = rows
            if rows < 50:
                reason = f"Insufficient OHLCV rows: {rows}"
                logger.warning("%s | rows=%s | %s", symbol, rows, reason)
                result.update(status='FETCH_FAILED', fetch_reason=reason, error=reason)
                return result

            technical_analysis = IndicatorsService.get_signal_analysis(data)
            if technical_analysis.get('technical_signal') == 'ERROR':
                reason = technical_analysis.get('details', 'Indicator analysis failed')
                logger.warning("%s | technical analysis error: %s", symbol, reason)
                result.update(
                    status='INDICATOR_FAILED',
                    technical_signal='ERROR',
                    rsi=technical_analysis.get('rsi', 0),
                    ema20=technical_analysis.get('ema_fast', 0),
                    ema50=technical_analysis.get('ema_slow', 0),
                    macd=technical_analysis.get('macd', 0),
                    technical_confidence=technical_analysis.get('confidence', 0),
                    indicator_reason=reason,
                    error=reason,
                )
                return result

            volume_profile = self.market_data_service.get_volume_profile(symbol)
            week_52 = self.market_data_service.get_52week_high_low(symbol)

            latest = data.iloc[-1]
            current_price = float(latest.get('close', 0))
            ema20 = float(technical_analysis.get('ema_fast', 0))
            ema50 = float(technical_analysis.get('ema_slow', 0))
            rsi = float(technical_analysis.get('rsi', 0))
            macd = float(technical_analysis.get('macd', 0))
            technical_signal = technical_analysis.get('technical_signal', 'UNKNOWN')

            result.update({
                'current_price': current_price,
                'technical_signal': technical_signal,
                'technical_confidence': technical_analysis.get('confidence', 0),
                'rsi': rsi,
                'ema20': ema20,
                'ema50': ema50,
                'macd': macd,
                'volume_ratio': volume_profile.get('volume_ratio', 0),
                'is_volume_breakout': volume_profile.get('is_breakout', False),
                'week_52_high': week_52.get('high_52week', 0),
                'week_52_low': week_52.get('low_52week', 0),
                'distance_from_high_percent': ((week_52.get('high_52week', 1) - current_price) / week_52.get('high_52week', 1) * 100) if week_52.get('high_52week') else 0,
                'distance_from_low_percent': ((current_price - week_52.get('low_52week', 0)) / week_52.get('low_52week', 1) * 100) if week_52.get('low_52week') else 0,
                'status': 'SCANNED',
            })

            logger.info(
                "Scanned %s | rows=%s | price=%s | RSI=%s | EMA20=%s | EMA50=%s | MACD=%s | signal=%s",
                symbol,
                rows,
                current_price,
                rsi,
                ema20,
                ema50,
                macd,
                technical_signal,
            )
            return result
        except Exception:
            trace = traceback.format_exc()
            logger.exception("Error scanning symbol %s", symbol)
            result.update(status='ERROR', error=trace)
            return result
    
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
