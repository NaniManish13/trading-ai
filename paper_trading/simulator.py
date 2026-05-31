"""
Paper Trading Simulator - Simulated trading engine
"""
import logging
from datetime import datetime
from typing import Dict, List, Optional
from services.portfolio import PortfolioService
from config.settings import STARTING_CAPITAL

logger = logging.getLogger(__name__)


class PaperTradingSimulator:
    """Paper trading simulation engine"""
    
    def __init__(self, starting_capital: float = STARTING_CAPITAL):
        """Initialize simulator"""
        self.portfolio = PortfolioService()
        self.portfolio.cash_balance = starting_capital
        self.starting_capital = starting_capital
        self.peak_value = starting_capital
        self.daily_pnl = 0
        self.session_start = datetime.now()
    
    def execute_buy(
        self,
        symbol: str,
        quantity: int,
        price: float,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        reasoning: str = "",
    ) -> Dict:
        """
        Execute a buy trade
        
        Args:
            symbol: Stock symbol
            quantity: Number of shares
            price: Price per share
            stop_loss: Stop loss price
            take_profit: Take profit price
            reasoning: Trade reasoning
        
        Returns:
            Dict with execution result
        """
        try:
            # Check if we already have this position
            if symbol in self.portfolio.positions:
                logger.warning(f"Position already exists for {symbol}")
                return {
                    'success': False,
                    'reason': 'Position already exists',
                    'symbol': symbol,
                }
            
            # Execute buy
            success = self.portfolio.add_position(
                symbol, quantity, price, stop_loss, take_profit
            )
            
            if success:
                return {
                    'success': True,
                    'symbol': symbol,
                    'side': 'BUY',
                    'quantity': quantity,
                    'price': price,
                    'cost': quantity * price,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'timestamp': datetime.now(),
                    'reasoning': reasoning,
                }
            else:
                return {
                    'success': False,
                    'reason': 'Insufficient cash',
                    'symbol': symbol,
                }
        except Exception as e:
            logger.error(f"Error executing buy: {e}")
            return {
                'success': False,
                'reason': str(e),
                'symbol': symbol,
            }
    
    def execute_sell(
        self,
        symbol: str,
        price: float,
        reasoning: str = "",
    ) -> Dict:
        """
        Execute a sell trade
        
        Args:
            symbol: Stock symbol
            price: Price per share
            reasoning: Trade reasoning
        
        Returns:
            Dict with execution result
        """
        try:
            if symbol not in self.portfolio.positions:
                return {
                    'success': False,
                    'reason': 'Position not found',
                    'symbol': symbol,
                }
            
            trade_result = self.portfolio.close_position(symbol, price)
            
            if trade_result:
                return {
                    'success': True,
                    'symbol': symbol,
                    'side': 'SELL',
                    **trade_result,
                    'timestamp': datetime.now(),
                    'reasoning': reasoning,
                }
            else:
                return {
                    'success': False,
                    'reason': 'Error closing position',
                    'symbol': symbol,
                }
        except Exception as e:
            logger.error(f"Error executing sell: {e}")
            return {
                'success': False,
                'reason': str(e),
                'symbol': symbol,
            }
    
    def update_positions(self, prices: Dict[str, float]) -> Dict:
        """
        Update all positions with current prices
        
        Args:
            prices: Dict of symbol -> price
        
        Returns:
            Dict with update summary
        """
        try:
            total_unrealized_pnl = 0
            updated_positions = []
            
            for symbol, price in prices.items():
                if symbol in self.portfolio.positions:
                    self.portfolio.update_position(symbol, price)
                    pos = self.portfolio.positions[symbol]
                    total_unrealized_pnl += pos['unrealized_pnl']
                    updated_positions.append({
                        'symbol': symbol,
                        'price': price,
                        'pnl': pos['unrealized_pnl'],
                        'pnl_percent': pos['unrealized_pnl_percent'],
                    })
            
            return {
                'total_unrealized_pnl': total_unrealized_pnl,
                'updated_positions': updated_positions,
                'timestamp': datetime.now(),
            }
        except Exception as e:
            logger.error(f"Error updating positions: {e}")
            return {}
    
    def get_summary(self) -> Dict:
        """Get trading summary"""
        try:
            portfolio_summary = self.portfolio.get_portfolio_summary()
            trade_stats = self.portfolio.get_trade_statistics()
            
            total_value = portfolio_summary['total_value']
            return_value = total_value - self.starting_capital
            return_percent = (return_value / self.starting_capital) * 100
            
            # Update peak value for drawdown calculation
            if total_value > self.peak_value:
                self.peak_value = total_value
            
            drawdown = ((self.peak_value - total_value) / self.peak_value) * 100
            
            return {
                'starting_capital': self.starting_capital,
                'current_value': total_value,
                'cash_balance': portfolio_summary['cash_balance'],
                'positions_value': portfolio_summary['positions_value'],
                'total_return': return_value,
                'return_percent': return_percent,
                'peak_value': self.peak_value,
                'drawdown': drawdown,
                'open_positions': portfolio_summary['total_positions'],
                'total_trades': trade_stats.get('total_trades', 0),
                'win_rate': trade_stats.get('win_rate', 0),
                'profit_factor': trade_stats.get('profit_factor', 0),
                'total_pnl': trade_stats.get('total_pnl', 0),
                'daily_pnl': self.portfolio.get_daily_pnl(),
                'timestamp': datetime.now(),
            }
        except Exception as e:
            logger.error(f"Error getting summary: {e}")
            return {}
    
    def get_positions(self) -> List[Dict]:
        """Get all open positions"""
        try:
            positions_list = []
            for symbol, pos in self.portfolio.positions.items():
                positions_list.append({
                    'symbol': symbol,
                    'quantity': pos['quantity'],
                    'entry_price': pos['entry_price'],
                    'current_price': pos['current_price'],
                    'current_value': pos['current_value'],
                    'unrealized_pnl': pos['unrealized_pnl'],
                    'unrealized_pnl_percent': pos['unrealized_pnl_percent'],
                    'entry_date': pos['entry_date'],
                    'stop_loss': pos.get('stop_loss'),
                    'take_profit': pos.get('take_profit'),
                })
            return positions_list
        except Exception as e:
            logger.error(f"Error getting positions: {e}")
            return []
    
    def get_trades(self, limit: int = 20) -> List[Dict]:
        """Get recent trades"""
        return self.portfolio.trades[-limit:]
