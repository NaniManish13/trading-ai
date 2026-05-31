"""
Portfolio management service
"""
import logging
from datetime import datetime
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from database.models import Portfolio, Position, Trade, Signal
from config.settings import STARTING_CAPITAL, RISK_PER_TRADE, DAILY_LOSS_LIMIT

logger = logging.getLogger(__name__)


class PortfolioService:
    """Manage portfolio positions and trades"""
    
    def __init__(self, db: Optional[Session] = None):
        """Initialize portfolio service"""
        self.db = db
        self.cash_balance = STARTING_CAPITAL
        self.positions = {}
        self.trades = []
    
    def get_portfolio_summary(self) -> Dict:
        """Get current portfolio summary"""
        total_positions_value = sum(p.get('current_value', 0) for p in self.positions.values())
        total_value = self.cash_balance + total_positions_value
        
        return {
            'cash_balance': self.cash_balance,
            'positions_value': total_positions_value,
            'total_value': total_value,
            'total_positions': len(self.positions),
            'total_trades': len(self.trades),
            'available_cash': self.cash_balance,
            'used_capital': total_positions_value,
        }
    
    def add_position(
        self,
        symbol: str,
        quantity: int,
        entry_price: float,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None
    ) -> bool:
        """Add a new position"""
        try:
            cost = quantity * entry_price
            if cost > self.cash_balance:
                logger.error(f"Insufficient cash for {symbol}")
                return False
            
            self.cash_balance -= cost
            
            self.positions[symbol] = {
                'quantity': quantity,
                'entry_price': entry_price,
                'current_price': entry_price,
                'current_value': cost,
                'entry_date': datetime.now(),
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'unrealized_pnl': 0,
                'unrealized_pnl_percent': 0,
            }
            
            logger.info(f"✓ Position added: {symbol} x{quantity} @ {entry_price}")
            return True
        except Exception as e:
            logger.error(f"Error adding position: {e}")
            return False
    
    def update_position(self, symbol: str, current_price: float) -> bool:
        """Update position with current price"""
        try:
            if symbol not in self.positions:
                return False
            
            pos = self.positions[symbol]
            pos['current_price'] = current_price
            pos['current_value'] = pos['quantity'] * current_price
            pos['unrealized_pnl'] = pos['current_value'] - (pos['quantity'] * pos['entry_price'])
            pos['unrealized_pnl_percent'] = (pos['unrealized_pnl'] / (pos['quantity'] * pos['entry_price'])) * 100
            
            return True
        except Exception as e:
            logger.error(f"Error updating position: {e}")
            return False
    
    def close_position(self, symbol: str, exit_price: float) -> Dict:
        """Close an open position"""
        try:
            if symbol not in self.positions:
                logger.error(f"Position not found: {symbol}")
                return {}
            
            pos = self.positions[symbol]
            quantity = pos['quantity']
            entry_price = pos['entry_price']
            
            # Calculate P&L
            pnl = (exit_price - entry_price) * quantity
            pnl_percent = (pnl / (entry_price * quantity)) * 100
            
            # Add cash back
            self.cash_balance += exit_price * quantity
            
            # Record trade
            trade = {
                'symbol': symbol,
                'entry_price': entry_price,
                'exit_price': exit_price,
                'quantity': quantity,
                'entry_date': pos['entry_date'],
                'exit_date': datetime.now(),
                'pnl': pnl,
                'pnl_percent': pnl_percent,
                'status': 'CLOSED',
                'stop_loss': pos.get('stop_loss'),
                'take_profit': pos.get('take_profit'),
            }
            
            self.trades.append(trade)
            del self.positions[symbol]
            
            logger.info(f"✓ Position closed: {symbol} | P&L: {pnl:.2f} ({pnl_percent:.2f}%)")
            return trade
        except Exception as e:
            logger.error(f"Error closing position: {e}")
            return {}
    
    def calculate_position_size(self, symbol: str, entry_price: float, stop_loss: float) -> int:
        """Calculate position size based on risk management"""
        try:
            portfolio_summary = self.get_portfolio_summary()
            total_value = portfolio_summary['total_value']
            
            # Risk per trade is 1% of portfolio
            risk_amount = total_value * RISK_PER_TRADE
            
            # Calculate stop loss distance
            stop_loss_distance = entry_price - stop_loss
            
            if stop_loss_distance <= 0:
                logger.error("Invalid stop loss")
                return 0
            
            # Position size = Risk amount / Stop loss distance
            quantity = int(risk_amount / stop_loss_distance)
            
            # Check if we have enough cash
            cost = quantity * entry_price
            if cost > self.cash_balance:
                quantity = int(self.cash_balance / entry_price)
            
            return max(quantity, 0)
        except Exception as e:
            logger.error(f"Error calculating position size: {e}")
            return 0
    
    def get_daily_pnl(self) -> float:
        """Get today's realized P&L"""
        today = datetime.now().date()
        today_trades = [
            t for t in self.trades 
            if t['exit_date'].date() == today
        ]
        return sum(t['pnl'] for t in today_trades)
    
    def get_trade_statistics(self) -> Dict:
        """Calculate trade statistics"""
        try:
            if not self.trades:
                return {
                    'total_trades': 0,
                    'win_rate': 0,
                    'avg_win': 0,
                    'avg_loss': 0,
                    'profit_factor': 0,
                    'total_pnl': 0,
                }
            
            closed_trades = [t for t in self.trades if t['status'] == 'CLOSED']
            winning_trades = [t for t in closed_trades if t['pnl'] > 0]
            losing_trades = [t for t in closed_trades if t['pnl'] < 0]
            
            total_wins = sum(t['pnl'] for t in winning_trades) if winning_trades else 0
            total_losses = abs(sum(t['pnl'] for t in losing_trades)) if losing_trades else 0
            
            return {
                'total_trades': len(closed_trades),
                'win_rate': (len(winning_trades) / len(closed_trades) * 100) if closed_trades else 0,
                'avg_win': (total_wins / len(winning_trades)) if winning_trades else 0,
                'avg_loss': (total_losses / len(losing_trades)) if losing_trades else 0,
                'profit_factor': (total_wins / total_losses) if total_losses > 0 else 0,
                'total_pnl': total_wins - total_losses,
            }
        except Exception as e:
            logger.error(f"Error calculating statistics: {e}")
            return {}
    
    def check_stop_loss_take_profit(self, symbol: str, current_price: float) -> str:
        """Check if stop loss or take profit is hit"""
        if symbol not in self.positions:
            return 'NONE'
        
        pos = self.positions[symbol]
        
        if pos.get('stop_loss') and current_price <= pos['stop_loss']:
            return 'STOP_LOSS'
        
        if pos.get('take_profit') and current_price >= pos['take_profit']:
            return 'TAKE_PROFIT'
        
        return 'NONE'
