"""
Sentiment analysis service using Google Gemini API
"""
import logging
import json
from typing import Dict, Optional
from config.settings import GEMINI_API_KEY

logger = logging.getLogger(__name__)

# Try to import Gemini API
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("google-generativeai not installed. Sentiment analysis will be limited.")


class SentimentService:
    """Analyze sentiment using Gemini API"""
    
    def __init__(self):
        """Initialize Gemini API"""
        if GEMINI_AVAILABLE and GEMINI_API_KEY:
            try:
                genai.configure(api_key=GEMINI_API_KEY)
                self.model = genai.GenerativeModel('gemini-pro')
                self.initialized = True
                logger.info("✓ Gemini API initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini API: {e}")
                self.initialized = False
        else:
            self.initialized = False
            logger.warning("Gemini API key not configured")
    
    def analyze_text_sentiment(self, text: str, symbol: str = "") -> Dict:
        """
        Analyze sentiment of financial text
        
        Args:
            text: Financial news or analysis text
            symbol: Stock symbol for context
        
        Returns:
            Dict with sentiment, confidence, and analysis
        """
        if not self.initialized:
            return self._mock_sentiment(text)
        
        try:
            prompt = f"""Analyze the sentiment of the following financial text about {symbol if symbol else "stocks"}.
            
Text: {text}

Provide response in this exact JSON format:
{{
    "sentiment": "POSITIVE" or "NEGATIVE" or "NEUTRAL",
    "confidence": 0.0-1.0,
    "key_points": ["point1", "point2", "point3"],
    "explanation": "brief explanation",
    "impact": "bullish" or "bearish" or "neutral"
}}

Only return valid JSON, no other text."""
            
            response = self.model.generate_content(prompt)
            
            # Parse response
            try:
                # Extract JSON from response
                response_text = response.text
                # Try to find JSON block
                if "{" in response_text:
                    json_start = response_text.find("{")
                    json_end = response_text.rfind("}") + 1
                    json_str = response_text[json_start:json_end]
                    result = json.loads(json_str)
                    return result
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse Gemini response: {response.text}")
                return self._mock_sentiment(text)
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment with Gemini: {e}")
            return self._mock_sentiment(text)
    
    def analyze_stock_news(self, title: str, content: str, symbol: str) -> Dict:
        """
        Analyze stock news
        
        Args:
            title: News title
            content: News content
            symbol: Stock symbol
        
        Returns:
            Dict with sentiment analysis
        """
        if not self.initialized:
            return self._mock_stock_analysis(title, content)
        
        try:
            full_text = f"Title: {title}\n\nContent: {content}"
            prompt = f"""Analyze this financial news about {symbol}:

{full_text}

Provide JSON response with:
{{
    "sentiment": "POSITIVE|NEGATIVE|NEUTRAL",
    "confidence": 0.0-1.0,
    "impact_on_stock": "bullish|bearish|neutral",
    "key_takeaways": ["point1", "point2"],
    "trading_implications": "brief implications for trading"
}}

Only return valid JSON."""
            
            response = self.model.generate_content(prompt)
            
            try:
                response_text = response.text
                if "{" in response_text:
                    json_start = response_text.find("{")
                    json_end = response_text.rfind("}") + 1
                    json_str = response_text[json_start:json_end]
                    result = json.loads(json_str)
                    return result
            except json.JSONDecodeError:
                logger.warning("Failed to parse stock analysis response")
                return self._mock_stock_analysis(title, content)
            
        except Exception as e:
            logger.error(f"Error analyzing stock news: {e}")
            return self._mock_stock_analysis(title, content)
    
    @staticmethod
    def _mock_sentiment(text: str) -> Dict:
        """Generate mock sentiment for testing (when API not available)"""
        # Simple keyword-based sentiment
        positive_words = ['profit', 'gain', 'bull', 'strong', 'outperform', 'beat', 'surge', 'rally']
        negative_words = ['loss', 'decline', 'bear', 'weak', 'underperform', 'miss', 'crash', 'fall']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            sentiment = "POSITIVE"
            impact = "bullish"
            confidence = 0.7
        elif negative_count > positive_count:
            sentiment = "NEGATIVE"
            impact = "bearish"
            confidence = 0.7
        else:
            sentiment = "NEUTRAL"
            impact = "neutral"
            confidence = 0.5
        
        return {
            "sentiment": sentiment,
            "confidence": confidence,
            "impact_on_stock": impact,
            "key_takeaways": ["Using mock sentiment analysis"],
            "trading_implications": "Configure GEMINI_API_KEY for real sentiment analysis"
        }
    
    @staticmethod
    def _mock_stock_analysis(title: str, content: str) -> Dict:
        """Mock stock analysis for testing"""
        return {
            "sentiment": "NEUTRAL",
            "confidence": 0.5,
            "impact_on_stock": "neutral",
            "key_takeaways": ["Mock analysis - configure Gemini API"],
            "trading_implications": "Real analysis requires GEMINI_API_KEY"
        }
