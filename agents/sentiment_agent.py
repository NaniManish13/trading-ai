"""
Sentiment Analysis Agent - Uses Gemini API for news analysis
"""
import logging
from typing import Dict, List
from services.sentiment import SentimentService

logger = logging.getLogger(__name__)


class SentimentAgent:
    """Sentiment analysis using Gemini API"""
    
    def __init__(self):
        """Initialize sentiment agent"""
        self.sentiment_service = SentimentService()
    
    def analyze_text(self, text: str, symbol: str = "") -> Dict:
        """
        Analyze sentiment of financial text
        
        Args:
            text: Financial news or analysis text
            symbol: Stock symbol for context
        
        Returns:
            Dict with sentiment analysis
        """
        try:
            result = self.sentiment_service.analyze_text_sentiment(text, symbol)
            
            # Normalize sentiment score
            sentiment_map = {
                'POSITIVE': 0.8,
                'NEGATIVE': -0.8,
                'NEUTRAL': 0,
            }
            
            sentiment = result.get('sentiment', 'NEUTRAL')
            confidence = result.get('confidence', 0.5)
            
            return {
                'symbol': symbol,
                'sentiment': sentiment,
                'sentiment_score': sentiment_map.get(sentiment, 0),
                'confidence': confidence,
                'impact': result.get('impact', 'neutral'),
                'key_points': result.get('key_points', []),
                'explanation': result.get('explanation', ''),
            }
        except Exception as e:
            logger.error(f"Error analyzing text sentiment: {e}")
            return {
                'symbol': symbol,
                'sentiment': 'NEUTRAL',
                'sentiment_score': 0,
                'confidence': 0,
                'impact': 'neutral',
                'key_points': [],
                'explanation': f'Error: {str(e)}',
            }
    
    def analyze_news(self, title: str, content: str, symbol: str) -> Dict:
        """
        Analyze financial news
        
        Args:
            title: News headline
            content: News content
            symbol: Stock symbol
        
        Returns:
            Dict with news analysis
        """
        try:
            result = self.sentiment_service.analyze_stock_news(title, content, symbol)
            
            sentiment_map = {
                'POSITIVE': 0.8,
                'NEGATIVE': -0.8,
                'NEUTRAL': 0,
            }
            
            sentiment = result.get('sentiment', 'NEUTRAL')
            
            return {
                'symbol': symbol,
                'title': title,
                'sentiment': sentiment,
                'sentiment_score': sentiment_map.get(sentiment, 0),
                'confidence': result.get('confidence', 0.5),
                'impact': result.get('impact_on_stock', 'neutral'),
                'takeaways': result.get('key_takeaways', []),
                'implications': result.get('trading_implications', ''),
            }
        except Exception as e:
            logger.error(f"Error analyzing news: {e}")
            return {
                'symbol': symbol,
                'title': title,
                'sentiment': 'NEUTRAL',
                'sentiment_score': 0,
                'confidence': 0,
                'impact': 'neutral',
                'takeaways': [],
                'implications': f'Error: {str(e)}',
            }
    
    def aggregate_sentiment(self, analyses: List[Dict]) -> Dict:
        """
        Aggregate multiple sentiment analyses
        
        Args:
            analyses: List of individual analyses
        
        Returns:
            Aggregated sentiment
        """
        try:
            if not analyses:
                return {
                    'overall_sentiment': 'NEUTRAL',
                    'overall_score': 0,
                    'confidence': 0,
                    'positive_count': 0,
                    'negative_count': 0,
                    'neutral_count': 0,
                }
            
            positive_count = sum(1 for a in analyses if a.get('sentiment') == 'POSITIVE')
            negative_count = sum(1 for a in analyses if a.get('sentiment') == 'NEGATIVE')
            neutral_count = sum(1 for a in analyses if a.get('sentiment') == 'NEUTRAL')
            
            avg_score = sum(a.get('sentiment_score', 0) for a in analyses) / len(analyses) if analyses else 0
            avg_confidence = sum(a.get('confidence', 0) for a in analyses) / len(analyses) if analyses else 0
            
            if positive_count > negative_count:
                overall_sentiment = 'POSITIVE'
            elif negative_count > positive_count:
                overall_sentiment = 'NEGATIVE'
            else:
                overall_sentiment = 'NEUTRAL'
            
            return {
                'overall_sentiment': overall_sentiment,
                'overall_score': avg_score,
                'confidence': avg_confidence,
                'positive_count': positive_count,
                'negative_count': negative_count,
                'neutral_count': neutral_count,
                'total_analyses': len(analyses),
            }
        except Exception as e:
            logger.error(f"Error aggregating sentiment: {e}")
            return {}
