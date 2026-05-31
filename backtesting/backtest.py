"""
Backtesting Module - Historical strategy testing
"""
import logging
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional
from services.market_data import MarketDataService
from services.indicators import IndicatorsService

logger = logging.getLogger(__name__)


class Backtester:
    """Backtest trading strategies"""
    
    def __init__(self):
        """Initialize backtester"""
        self.market_data_service = MarketDataService()
        self.indicators_service = IndicatorsService()
    
    def run_backtest(
        self,
        symbol: str,
        strategy_func,
        initial_capital: float = 100000,
        period: str = "1y",
        **kwargs
    ) -> Dict:
        """
        Run backtest on historical data
        
        Args:
            symbol: Stock symbol
            strategy_func: Strategy function that takes OHLCV data and returns signals
            initial_capital: Starting capital
            period: Data period
            **kwargs: Additional strategy parameters
        
        Returns:
            Dict with backtest results
        """
        try:
            # Fetch data
            data = self.market_data_service.get_ohlcv(symbol, period=period)
            if data.empty or len(data) < 50:
                return {'error': 'Insufficient data'}
            
            # Add technical indicators
            data = self.indicators_service.get_all_indicators(data)
            
            # Run strategy
            trades = strategy_func(data, **kwargs)
            
            # Calculate statistics
            stats = self._calculate_backtest_stats(
                data, trades, initial_capital, symbol
            )
            
            return stats
        except Exception as e:
            logger.error(f"Error running backtest: {e}")
            return {'error': str(e)}
    
    def _calculate_backtest_stats(
        self,
        data: pd.DataFrame,
        trades: List[Dict],
        initial_capital: float,
        symbol: str
    ) -> Dict:
        """Calculate backtest statistics"""
        try:
            if not trades:
                return {
                    'symbol': symbol,
                    'total_return': 0,
                    'cagr': 0,
                    'sharpe_ratio': 0,
                    'max_drawdown': 0,
                    'win_rate': 0,
                    'total_trades': 0,
                }
            
            # Process trades
            capital = initial_capital
            portfolio_values = [initial_capital]
            
            for trade in trades:
                if trade.get('side') == 'BUY':
                    cost = trade.get('quantity', 0) * trade.get('price', 0)
                    capital -= cost
                elif trade.get('side') == 'SELL':
                    revenue = trade.get('quantity', 0) * trade.get('price', 0)
                    capital += revenue
                
                portfolio_values.append(capital)
            
            final_value = portfolio_values[-1] if portfolio_values else initial_capital
            
            # Calculate metrics
            total_return = (final_value - initial_capital) / initial_capital
            
            # CAGR
            start_date = data.index[0]
            end_date = data.index[-1]
            days = (end_date - start_date).days
            years = days / 365.25
            cagr = (final_value / initial_capital) ** (1 / years) - 1 if years > 0 else 0
            
            # Sharpe Ratio
            returns = pd.Series(portfolio_values).pct_change()
            sharpe_ratio = returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0
            
            # Max Drawdown
            cummax = np.maximum.accumulate(portfolio_values)
            drawdown = (np.array(portfolio_values) - cummax) / cummax
            max_drawdown = np.min(drawdown)
            
            # Win rate
            winning_trades = sum(1 for t in trades if t.get('pnl', 0) > 0)
            total_trades = len(trades)
            win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
            
            # Avg win/loss
            wins = [t.get('pnl', 0) for t in trades if t.get('pnl', 0) > 0]
            losses = [abs(t.get('pnl', 0)) for t in trades if t.get('pnl', 0) < 0]
            avg_win = np.mean(wins) if wins else 0
            avg_loss = np.mean(losses) if losses else 0
            
            # Profit factor
            total_wins = sum(wins)
            total_losses = sum(losses)
            profit_factor = (total_wins / total_losses) if total_losses > 0 else 0
            
            return {
                'symbol': symbol,
                'start_date': str(start_date.date()),
                'end_date': str(end_date.date()),
                'initial_capital': initial_capital,
                'final_capital': final_value,
                'total_return': total_return,
                'total_return_percent': total_return * 100,
                'cagr': cagr,
                'cagr_percent': cagr * 100,
                'sharpe_ratio': sharpe_ratio,
                'max_drawdown': max_drawdown,
                'max_drawdown_percent': max_drawdown * 100,
                'total_trades': total_trades,
                'win_rate': win_rate,
                'avg_win': avg_win,
                'avg_loss': avg_loss,
                'profit_factor': profit_factor,
                'total_wins': total_wins,
                'total_losses': total_losses,
            }
        except Exception as e:
            logger.error(f"Error calculating stats: {e}")
            return {}
    
    def simple_ema_strategy(self, data: pd.DataFrame, **kwargs) -> List[Dict]:
        """
        Simple EMA crossover strategy for backtesting
        
        Args:
            data: OHLCV data with indicators
            **kwargs: Strategy parameters
        
        Returns:
            List of trades
        """
        try:
            trades = []
            position = None
            
            for i in range(1, len(data)):
                ema_fast = data['ema_fast'].iloc[i]
                ema_slow = data['ema_slow'].iloc[i]
                prev_ema_fast = data['ema_fast'].iloc[i-1]
                prev_ema_slow = data['ema_slow'].iloc[i-1]
                price = data['close'].iloc[i]
                
                # Buy signal: fast EMA crosses above slow EMA
                if prev_ema_fast <= prev_ema_slow and ema_fast > ema_slow:
                    if position is None:
                        position = {
                            'side': 'BUY',
                            'price': price,
                            'date': data.index[i],
                            'quantity': 1,
                        }
                
                # Sell signal: fast EMA crosses below slow EMA
                elif prev_ema_fast >= prev_ema_slow and ema_fast < ema_slow:
                    if position:
                        pnl = (price - position['price']) * position['quantity']
                        position['exit_price'] = price
                        position['exit_date'] = data.index[i]
                        position['side'] = 'SELL'
                        position['pnl'] = pnl
                        trades.append(position)
                        position = None
            
            return trades
        except Exception as e:
            logger.error(f"Error running EMA strategy: {e}")
            return []
    
    def rsi_strategy(self, data: pd.DataFrame, **kwargs) -> List[Dict]:
        """
        RSI-based strategy for backtesting
        
        Args:
            data: OHLCV data with indicators
            **kwargs: Strategy parameters
        
        Returns:
            List of trades
        """
        try:
            trades = []
            position = None
            rsi_oversold = kwargs.get('rsi_oversold', 30)
            rsi_overbought = kwargs.get('rsi_overbought', 70)
            
            for i in range(1, len(data)):
                rsi = data['rsi'].iloc[i]
                price = data['close'].iloc[i]
                
                # Buy signal: RSI below oversold level
                if rsi < rsi_oversold:
                    if position is None:
                        position = {
                            'side': 'BUY',
                            'price': price,
                            'date': data.index[i],
                            'quantity': 1,
                        }
                
                # Sell signal: RSI above overbought level
                elif rsi > rsi_overbought:
                    if position:
                        pnl = (price - position['price']) * position['quantity']
                        position['exit_price'] = price
                        position['exit_date'] = data.index[i]
                        position['side'] = 'SELL'
                        position['pnl'] = pnl
                        trades.append(position)
                        position = None
            
            return trades
        except Exception as e:
            logger.error(f"Error running RSI strategy: {e}")
            return []
