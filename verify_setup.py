from config.settings import *
from database.models import *
from database.connection import init_db
from services.market_data import MarketDataService
from services.indicators import IndicatorsService
from services.sentiment import SentimentService
from services.portfolio import PortfolioService
from agents.market_scanner import MarketScannerAgent
from agents.technical_agent import TechnicalAgent
from agents.sentiment_agent import SentimentAgent
from agents.risk_agent import RiskAgent
from agents.decision_agent import DecisionAgent
from paper_trading.simulator import PaperTradingSimulator
from paper_trading.journal import TradeJournal
from backtesting.backtest import Backtester

print('✓ All imports successful!')
print('✓ Configuration loaded')
print('✓ Initializing database...')
init_db()
print('✓ Database initialized!')
print('✓ Platform ready to launch!')
