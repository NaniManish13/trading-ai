"""
Decision Agent - Aggregates all agent outputs and makes trading decisions
"""
import logging
from typing import Dict
from agents.market_scanner import MarketScannerAgent
from agents.technical_agent import TechnicalAgent
from agents.sentiment_agent import SentimentAgent
from agents.risk_agent import RiskAgent

logger = logging.getLogger(__name__)


class DecisionAgent:
    """Aggregates all agent signals and makes trading decisions"""
    
    def __init__(self):
        """Initialize decision agent"""
        self.market_scanner = MarketScannerAgent()
        self.technical_agent = TechnicalAgent()
        self.sentiment_agent = SentimentAgent()
        self.risk_agent = RiskAgent()
    
    def make_decision(
        self,
        symbol: str,
        current_price: float,
        portfolio_value: float,
        sentiment_text: str = "",
        daily_loss: float = 0,
    ) -> Dict:
        """
        Make trading decision based on all agents
        
        Args:
            symbol: Stock symbol
            current_price: Current stock price
            portfolio_value: Current portfolio value
            sentiment_text: Optional sentiment context
            daily_loss: Current daily loss
        
        Returns:
            Dict with trading decision
        """
        try:
            # Get technical analysis
            technical_analysis = self.technical_agent.analyze(symbol)
            
            # Get sentiment analysis
            sentiment_analysis = {}
            if sentiment_text:
                sentiment_analysis = self.sentiment_agent.analyze_text(sentiment_text, symbol)
            
            # Calculate stop loss based on technical levels
            technical_details = technical_analysis.get('details', {})
            atr = technical_details.get('atr', current_price * 0.02)
            stop_loss = current_price - (atr * 2)
            
            # Get risk analysis
            risk_analysis = self.risk_agent.evaluate_trade(
                symbol, current_price, stop_loss, portfolio_value, daily_loss
            )
            
            # Aggregate signals
            decision = self._aggregate_signals(
                technical_analysis,
                sentiment_analysis,
                risk_analysis,
                symbol,
                current_price,
                stop_loss
            )
            
            return decision
        except Exception as e:
            logger.error(f"Error making decision: {e}")
            return {
                'symbol': symbol,
                'decision': 'HOLD',
                'confidence': 0,
                'reasoning': f'Error: {str(e)}',
                'technical_signal': 'ERROR',
                'sentiment_signal': 'ERROR',
                'risk_approved': False,
            }
    
    def _aggregate_signals(
        self,
        technical: Dict,
        sentiment: Dict,
        risk: Dict,
        symbol: str,
        price: float,
        stop_loss: float,
    ) -> Dict:
        """
        Aggregate signals from all agents
        
        Args:
            technical: Technical analysis result
            sentiment: Sentiment analysis result
            risk: Risk analysis result
            symbol: Stock symbol
            price: Current price
            stop_loss: Calculated stop loss
        
        Returns:
            Aggregated decision
        """
        try:
            # Extract signals
            technical_signal = technical.get('signal', 'HOLD')
            technical_confidence = technical.get('confidence', 0)
            
            sentiment_signal = sentiment.get('sentiment', 'NEUTRAL') if sentiment else 'NEUTRAL'
            sentiment_score = sentiment.get('sentiment_score', 0) if sentiment else 0
            
            risk_approved = risk.get('approved', False)
            position_size = risk.get('position_size', 0)
            
            # Calculate weights
            weights = {
                'technical': 0.5,
                'sentiment': 0.2,
                'risk': 0.3,
            }
            
            # Calculate decision score
            technical_score = 1.0 if technical_signal == 'BUY' else (-1.0 if technical_signal == 'SELL' else 0)
            sentiment_score_norm = sentiment_score / 0.8 if sentiment_score != 0 else 0  # Normalize
            risk_score = 1.0 if risk_approved else -1.0
            
            final_score = (
                technical_score * weights['technical'] * technical_confidence +
                sentiment_score_norm * weights['sentiment'] +
                risk_score * weights['risk']
            )
            
            # Make decision
            if final_score > 0.3 and risk_approved:
                decision = 'BUY'
            elif final_score < -0.3 and risk_approved:
                decision = 'SELL'
            else:
                decision = 'HOLD'
            
            # Calculate confidence
            confidence = min(abs(final_score), 1.0)
            
            # Build reasoning
            reasoning = self._build_reasoning(
                technical, sentiment, risk, decision
            )
            
            return {
                'symbol': symbol,
                'decision': decision,
                'confidence': confidence,
                'final_score': final_score,
                'reasoning': reasoning,
                'technical_signal': technical_signal,
                'technical_confidence': technical_confidence,
                'sentiment_signal': sentiment_signal,
                'risk_approved': risk_approved,
                'position_size': position_size,
                'entry_price': price,
                'stop_loss': stop_loss,
                'take_profit': price + ((price - stop_loss) * 2),  # 2:1 risk/reward
                'components': {
                    'technical': technical,
                    'sentiment': sentiment,
                    'risk': risk,
                }
            }
        except Exception as e:
            logger.error(f"Error aggregating signals: {e}")
            return {}
    
    def _build_reasoning(
        self,
        technical: Dict,
        sentiment: Dict,
        risk: Dict,
        decision: str
    ) -> str:
        """Build human-readable reasoning for decision"""
        reasons = []
        
        # Technical reasoning
        tech_signal = technical.get('signal', 'HOLD')
        reasons.append(f"Technical: {tech_signal} ({technical.get('confidence', 0):.2%})")
        
        # Sentiment reasoning
        if sentiment:
            sent = sentiment.get('sentiment', 'NEUTRAL')
            reasons.append(f"Sentiment: {sent}")
        
        # Risk reasoning
        risk_approved = risk.get('approved', False)
        reasons.append(f"Risk: {'APPROVED' if risk_approved else 'REJECTED'} ({risk.get('reason', '')})")
        
        return " | ".join(reasons)
    
    def get_market_opportunities(self) -> Dict:
        """
        Scan market and get top opportunities
        
        Args:
            None
        
        Returns:
            Dict with top trading opportunities
        """
        try:
            scan_results = self.market_scanner.scan_market()
            opportunities = scan_results.get('opportunities', [])
            top_opportunities = self.market_scanner.get_top_opportunities(opportunities, limit=5)
            
            return {
                'total_scanned': scan_results.get('total_scanned', 0),
                'successful_fetches': scan_results.get('successful_fetches', 0),
                'failed_fetches': scan_results.get('failed_fetches', 0),
                'indicator_failures': scan_results.get('indicator_failures', 0),
                'total_opportunities': scan_results.get('total_opportunities', 0),
                'top_opportunities': top_opportunities,
                'errors': scan_results.get('errors', []),
                'scan_log': scan_results.get('scan_log', []),
                'timestamp': scan_results.get('timestamp'),
            }
        except Exception as e:
            logger.exception(f"Error getting market opportunities: {e}")
            return {
                'total_scanned': 0,
                'successful_fetches': 0,
                'failed_fetches': 0,
                'indicator_failures': 0,
                'total_opportunities': 0,
                'top_opportunities': [],
                'errors': [{'error': str(e)}],
                'scan_log': [],
                'timestamp': None,
            }
