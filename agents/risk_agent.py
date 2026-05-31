"""
Risk Management Agent - Evaluates trade risk and sizing
"""
import logging
from typing import Dict, Tuple
from config.settings import (
    RISK_PER_TRADE, DAILY_LOSS_LIMIT, MAX_DRAWDOWN, STARTING_CAPITAL
)

logger = logging.getLogger(__name__)


class RiskAgent:
    """Risk management and position sizing"""
    
    def __init__(self):
        """Initialize risk agent"""
        self.risk_per_trade = RISK_PER_TRADE
        self.daily_loss_limit = DAILY_LOSS_LIMIT
        self.max_drawdown = MAX_DRAWDOWN
        self.starting_capital = STARTING_CAPITAL
    
    def evaluate_trade(
        self,
        symbol: str,
        entry_price: float,
        stop_loss: float,
        portfolio_value: float,
        daily_loss: float = 0,
    ) -> Dict:
        """
        Evaluate risk for a trade
        
        Args:
            symbol: Stock symbol
            entry_price: Entry price
            stop_loss: Stop loss price
            portfolio_value: Current portfolio value
            daily_loss: Current daily loss
        
        Returns:
            Dict with risk analysis
        """
        try:
            # Calculate risk amount
            risk_amount = portfolio_value * self.risk_per_trade
            
            # Calculate stop loss distance
            stop_loss_distance = entry_price - stop_loss
            
            if stop_loss_distance <= 0:
                return {
                    'symbol': symbol,
                    'approved': False,
                    'reason': 'Invalid stop loss - must be below entry price',
                    'risk_score': 0,
                    'position_size': 0,
                }
            
            # Calculate position size
            position_size = int(risk_amount / stop_loss_distance)
            position_cost = position_size * entry_price
            
            # Check daily loss limit
            if daily_loss + risk_amount > portfolio_value * self.daily_loss_limit:
                return {
                    'symbol': symbol,
                    'approved': False,
                    'reason': 'Would exceed daily loss limit',
                    'risk_score': 0.3,
                    'position_size': 0,
                    'daily_loss_percent': ((daily_loss + risk_amount) / portfolio_value) * 100,
                    'daily_limit_percent': self.daily_loss_limit * 100,
                }
            
            # Calculate risk score
            risk_score = self._calculate_risk_score(
                entry_price, stop_loss, portfolio_value, position_cost
            )
            
            return {
                'symbol': symbol,
                'approved': True,
                'reason': 'Trade approved',
                'risk_score': risk_score,
                'position_size': position_size,
                'position_cost': position_cost,
                'risk_amount': risk_amount,
                'stop_loss_distance': stop_loss_distance,
                'stop_loss_percent': (stop_loss_distance / entry_price) * 100,
                'portfolio_utilization': (position_cost / portfolio_value) * 100,
            }
        except Exception as e:
            logger.error(f"Error evaluating trade: {e}")
            return {
                'symbol': symbol,
                'approved': False,
                'reason': f'Error: {str(e)}',
                'risk_score': 0,
                'position_size': 0,
            }
    
    def _calculate_risk_score(
        self,
        entry_price: float,
        stop_loss: float,
        portfolio_value: float,
        position_cost: float
    ) -> float:
        """
        Calculate risk score (0-1, lower is better)
        
        Args:
            entry_price: Entry price
            stop_loss: Stop loss price
            portfolio_value: Portfolio value
            position_cost: Total position cost
        
        Returns:
            Risk score
        """
        try:
            # Risk/reward ratio component
            risk_percent = ((entry_price - stop_loss) / entry_price) * 100
            risk_ratio_component = min(risk_percent / 5, 1)  # Normalize to 0-1
            
            # Position size component
            position_percent = (position_cost / portfolio_value) * 100
            position_component = min(position_percent / 10, 1)  # Normalize to 0-1
            
            # Combined score
            risk_score = (risk_ratio_component + position_component) / 2
            
            return min(risk_score, 1.0)
        except Exception as e:
            logger.error(f"Error calculating risk score: {e}")
            return 1.0
    
    def check_daily_loss_limit(
        self,
        daily_loss: float,
        portfolio_value: float
    ) -> Tuple[bool, str]:
        """
        Check if daily loss limit is exceeded
        
        Args:
            daily_loss: Today's loss
            portfolio_value: Current portfolio value
        
        Returns:
            Tuple of (approved, reason)
        """
        daily_loss_percent = abs(daily_loss) / portfolio_value
        
        if daily_loss_percent >= self.daily_loss_limit:
            return False, f"Daily loss limit ({self.daily_loss_limit*100:.1f}%) exceeded"
        
        return True, "Daily loss limit OK"
    
    def check_max_drawdown(
        self,
        peak_value: float,
        current_value: float
    ) -> Tuple[bool, str]:
        """
        Check if max drawdown is exceeded
        
        Args:
            peak_value: Peak portfolio value
            current_value: Current portfolio value
        
        Returns:
            Tuple of (approved, reason)
        """
        if peak_value == 0:
            return True, "No peak value set"
        
        drawdown = (current_value - peak_value) / peak_value
        
        if drawdown <= -self.max_drawdown:
            return False, f"Max drawdown ({self.max_drawdown*100:.1f}%) exceeded"
        
        return True, "Max drawdown OK"
    
    def validate_position_sizing(
        self,
        position_size: int,
        entry_price: float,
        available_capital: float
    ) -> Tuple[bool, str]:
        """
        Validate position sizing
        
        Args:
            position_size: Number of shares
            entry_price: Entry price per share
            available_capital: Available cash
        
        Returns:
            Tuple of (valid, reason)
        """
        cost = position_size * entry_price
        
        if cost > available_capital:
            return False, f"Insufficient capital: need {cost:.2f}, have {available_capital:.2f}"
        
        if position_size <= 0:
            return False, "Position size must be positive"
        
        return True, "Position sizing valid"
    
    def get_recommended_position_size(
        self,
        entry_price: float,
        stop_loss: float,
        portfolio_value: float,
    ) -> int:
        """
        Get recommended position size
        
        Args:
            entry_price: Entry price
            stop_loss: Stop loss price
            portfolio_value: Portfolio value
        
        Returns:
            Recommended position size
        """
        try:
            risk_amount = portfolio_value * self.risk_per_trade
            stop_loss_distance = entry_price - stop_loss
            
            if stop_loss_distance <= 0:
                return 0
            
            position_size = int(risk_amount / stop_loss_distance)
            return max(position_size, 0)
        except Exception as e:
            logger.error(f"Error getting position size: {e}")
            return 0
